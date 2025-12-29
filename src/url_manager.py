from urllib.parse import urlparse
from .logger import setup_logger

logger = setup_logger(__name__)

class UrlManager:
    """
    URLの管理（正規化、バリデーション、状態管理）を行うクラス。
    """
    def __init__(self, start_url: str, max_pages: int = 20):
        self.start_url = self.normalize_url(start_url)
        self.domain = urlparse(self.start_url).netloc
        self.base_path = urlparse(self.start_url).path if urlparse(self.start_url).path else "/"
        self.max_pages = max_pages
        
        self.visited = set()
        self.discovered = set()
        self.discovered.add(self.start_url)
        self.limit_reached_logged = False

    def normalize_url(self, url: str) -> str:
        """
        URLからフラグメントを除去して正規化します。
        """
        parsed = urlparse(url)
        return parsed._replace(fragment='').geturl()

    def is_valid_url(self, url: str) -> bool:
        """
        URLがクロール対象（同一ドメインかつhttp/https、ベースパス配下）かどうかを判定します。
        """
        parsed = urlparse(url)
        
        # ドメインの一致を確認
        if parsed.netloc != self.domain:
            return False
            
        # http/httpsスキームのみを対象とする
        if parsed.scheme not in ('http', 'https'):
            return False
            
        # ベースパス内にあるか確認
        if not parsed.path.startswith(self.base_path):
            return False
            
        return True

    def can_crawl(self, url: str) -> bool:
        """
        指定されたURLがクロール可能か（未訪問かつ制限内か）を判定します。
        """
        # 既に訪問済みならスキップ
        if url in self.visited:
            return False

        # ページ数制限チェック
        if len(self.visited) >= self.max_pages:
            if not self.limit_reached_logged:
                logger.warning(f"最大クロールページ数 {self.max_pages} を超えました。クロールを中止します。")
                self.limit_reached_logged = True
            return False
            
        return True

    def mark_visited(self, url: str):
        """
        URLを訪問済みにマークします。
        """
        self.visited.add(url)

    def add_discovered_url(self, url: str) -> bool:
        """
        新しいURLを発見リストに追加します。
        新規URLでかつ有効なURLであれば True を返します。
        """
        normalized = self.normalize_url(url)
        
        if not self.is_valid_url(normalized):
            return False
            
        if normalized in self.discovered:
            return False
            
        self.discovered.add(normalized)
        return True
