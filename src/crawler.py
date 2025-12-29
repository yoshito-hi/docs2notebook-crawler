import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin
from .logger import setup_logger
from .extractor import ContentExtractor

logger = setup_logger(__name__)

class DocsCrawler:
    """
    指定されたベースURLから開始し、同一ドメイン内のドキュメントページをクロールするクラス。
    """
    def __init__(self, start_url: str, output_file: str, max_concurrent: int = 5, max_pages: int = 20):
        self.start_url = start_url
        self.output_file = output_file
        self.domain = urlparse(start_url).netloc
        self.visited = set()
        self.queue = asyncio.Queue()
        self.extractor = ContentExtractor()

        # 結果をメモリに保持せず、直接ファイルに書き込むためのロック
        self.file_lock = asyncio.Lock()
        self.max_concurrent = max_concurrent
        self.max_pages = max_pages
        self.base_path = urlparse(start_url).path if urlparse(start_url).path else "/"
        self.limit_reached_logged = False
        self.discovered = set()
        self.discovered.add(self.start_url)

    def _is_valid_url(self, url: str) -> bool:
        """
        URLがクロール対象（同一ドメインかつhttp/https）かどうかを判定します。
        """
        parsed = urlparse(url)
        # ドメインの一致を確認
        if parsed.netloc != self.domain:
            return False
        # http/httpsスキームのみを対象とする
        if parsed.scheme not in ('http', 'https'):
            return False
            
        # ベースパス内にあるか確認 (例: /docs/ で開始した場合は /docs/ 配下のみ)
        if not parsed.path.startswith(self.base_path):
            return False
            
        return True

    def _normalize_url(self, url: str) -> str:
        """
        URLからフラグメントを除去して正規化します。
        """
        parsed = urlparse(url)
        return parsed._replace(fragment='').geturl()

    async def crawl_page(self, context, url):
        """
        単一のページをクロールし、コンテンツを抽出して新しいリンクを見つけます。
        """
        if url in self.visited:
            return
            
        # ページ数制限チェック
        if len(self.visited) >= self.max_pages:
            if not self.limit_reached_logged:
                logger.warning(f"最大クロールページ数 {self.max_pages} を超えました。クロールを中止します。")
                self.limit_reached_logged = True
            return

        self.visited.add(url)
        
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
                # 正規化して有効性を確認
                normalized = self._normalize_url(href)
                if self._is_valid_url(normalized):
                    self.discovered.add(normalized)
                    if normalized not in self.visited:
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
            self.queue.put_nowait(self._normalize_url(self.start_url))
            
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
        crawled_count = len(self.visited)
        uncrawled = self.discovered - self.visited
        uncrawled_count = len(uncrawled)
        
        # 結果サマリーはloggingではなくprintを使用して、見やすく整形表示する
        print("\n" + "-" * 40)
        print(f"📈 クロール完了サマリー")
        print("-" * 40)
        print(f"探索したページ総数: {crawled_count}")
        print("探索したページ一覧:")
        for url in sorted(self.visited):
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
        first_url = await self.queue.get()
        
        # 最初のタスクを作成
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
                if url not in self.visited:
                    new_task = asyncio.create_task(fetch(url))
                    tasks.add(new_task)
