import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin
import logging
from .extractor import ContentExtractor

logger = logging.getLogger(__name__)

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
        self.results = []
        self.max_concurrent = max_concurrent
        self.max_pages = max_pages
        self.base_path = urlparse(start_url).path if urlparse(start_url).path else "/"

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
            logger.warning(f"最大クロールページ数 {self.max_pages} を超えました。クロールを中止します。")
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
            self.results.append((url, markdown))
            
            # リンクの探索
            hrefs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
            }''')
            
            for href in hrefs:
                # 正規化して有効性を確認
                normalized = self._normalize_url(href)
                if self._is_valid_url(normalized) and normalized not in self.visited:
                    await self.queue.put(normalized)
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
        finally:
            await page.close()

    async def run(self):
        """
        クローラーのメイン実行メソッド。
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # キューを初期化
            self.queue.put_nowait(self._normalize_url(self.start_url))
            
            # キューの処理を開始
            await self.process_queue(context)

            await browser.close()
            
        # 結果をファイルに保存
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for _, md in self.results:
                f.write(md)
        logger.info(f"{len(self.results)} ページをクロールし、{self.output_file} に保存しました。")

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
