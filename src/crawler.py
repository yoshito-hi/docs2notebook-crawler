import asyncio
from playwright.async_api import async_playwright
from .logger import setup_logger
from .extractor import ContentExtractor
from .url_manager import UrlManager

logger = setup_logger(__name__)

class DocsCrawler:
    """
    指定されたベースURLから開始し、同一ドメイン内のドキュメントページをクロールするクラス。
    """
    def __init__(self, start_url: str, output_file: str, max_concurrent: int = 5, max_pages: int = 20):
        self.output_file = output_file
        self.max_concurrent = max_concurrent
        
        # URL管理とコンテンツ抽出の委譲
        self.url_manager = UrlManager(start_url, max_pages)
        self.extractor = ContentExtractor()
        
        self.queue = asyncio.Queue()
        # 結果をメモリに保持せず、直接ファイルに書き込むためのロック
        self.file_lock = asyncio.Lock()

    async def crawl_page(self, context, url):
        """
        単一のページをクロールし、コンテンツを抽出して新しいリンクを見つけます。
        """
        if not self.url_manager.can_crawl(url):
            return

        self.url_manager.mark_visited(url)
        logger.info(f"クロール中: {url}")
        
        page = await context.new_page()
        try:
            # ページに移動し、ネットワークがアイドル状態になるまで待機（SPA対応）
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # コンテンツの抽出
            content = await page.content()
            markdown = self.extractor.extract(content, url)
            
            # 結果を即座にファイルに保存（メモリ節約）
            await self._save_page_content(markdown)
            
            # リンクの探索
            hrefs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
            }''')
            
            for href in hrefs:
                if self.url_manager.add_discovered_url(href):
                    # 正規化されたURLが返されるわけではないので、add_discovered_url内で正規化しつつ
                    # 再度取得する必要があるが、add_discovered_urlはboolを返すのみ。
                    # ここでは normalize してから queue に入れる。
                    normalized = self.url_manager.normalize_url(href)
                    if normalized not in self.url_manager.visited:
                        await self.queue.put(normalized)
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
        finally:
            await page.close()

    async def _save_page_content(self, content: str):
        """
        スレッドセーフにファイルへ追記します。
        """
        async with self.file_lock:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(content)

    async def run(self):
        """
        クローラーのメイン実行メソッド。
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # キューを初期化
            self.queue.put_nowait(self.url_manager.start_url)
            
            # 出力ファイルを初期化（空にする）
            with open(self.output_file, 'w', encoding='utf-8') as f:
                pass
            
            # キューの処理を開始
            await self.process_queue(context)

            await browser.close()
            
        self._log_summary()

    def _log_summary(self):
        """
        クロール結果のサマリーを標準出力に表示します（ログ形式ではない）。
        """
        visited = self.url_manager.visited
        discovered = self.url_manager.discovered
        
        crawled_count = len(visited)
        uncrawled = discovered - visited
        uncrawled_count = len(uncrawled)
        
        # 結果サマリーはloggingではなくprintを使用して、見やすく整形表示する
        print("\n" + "-" * 40)
        print(f"📈 クロール完了サマリー")
        print("-" * 40)
        print(f"探索したページ総数: {crawled_count}")
        print("探索したページ一覧:")
        for url in sorted(visited):
            print(f"  - {url}")
            
        print("-" * 40)
        print(f"発見されたが未探索のページ総数: {uncrawled_count}")
        if uncrawled_count > 0:
            print("発見されたが未探索のページ一覧:")
            for url in sorted(uncrawled):
                print(f"  - {url}")
        print("-" * 40)
        print(f"結果は {self.output_file} に保存されました。")

    async def process_queue(self, context):
        """
        非同期のセマフォを使用して、並行性を制限しながらキュー内のURLを処理します。
        """
        sem = asyncio.Semaphore(self.max_concurrent)
        
        # 実行中のタスクを追跡
        tasks = set()
        
        async def fetch(url):
            async with sem:
                await self.crawl_page(context, url)
        
        # 最初のURLを取得
        if not self.queue.empty():
            first_url = await self.queue.get()
            task = asyncio.create_task(fetch(first_url))
            tasks.add(task)
        
        while tasks:
            # いずれかのタスクが完了するのを待機
            done, pending_tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks = pending_tasks
            
            for t in done:
                try:
                    await t
                except Exception as e:
                    logger.error(f"タスクエラー: {e}")

            # キューを空にして新しいタスクを作成
            while not self.queue.empty():
                url = self.queue.get_nowait()
                # ここでの visited チェックは queue に入れる前に行っているが、念のため
                if url not in self.url_manager.visited:
                    new_task = asyncio.create_task(fetch(url))
                    tasks.add(new_task)
