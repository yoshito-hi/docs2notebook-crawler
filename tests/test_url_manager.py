import unittest
import sys
import os

# srcをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.url_manager import UrlManager

class TestUrlManager(unittest.TestCase):
    def setUp(self):
        self.start_url = "https://example.com/docs/"
        self.manager = UrlManager(self.start_url, max_pages=5)

    def test_normalize_url(self):
        url = "https://example.com/docs/page1#section"
        expected = "https://example.com/docs/page1"
        self.assertEqual(self.manager.normalize_url(url), expected)

    def test_is_valid_url(self):
        # 有効なURL
        self.assertTrue(self.manager.is_valid_url("https://example.com/docs/page1"))
        
        # 異なるドメイン
        self.assertFalse(self.manager.is_valid_url("https://other.com/docs/page1"))
        
        # 異なるパス（ベースパス外）
        self.assertFalse(self.manager.is_valid_url("https://example.com/about"))
        
        # 非HTTP
        self.assertFalse(self.manager.is_valid_url("ftp://example.com/docs/page1"))

    def test_can_crawl(self):
        url = "https://example.com/docs/page1"
        
        # 初回はTrue
        self.assertTrue(self.manager.can_crawl(url))
        
        # 訪問済みにする
        self.manager.mark_visited(url)
        
        # 訪問済みなのでFalse
        self.assertFalse(self.manager.can_crawl(url))

    def test_max_pages(self):
        for i in range(5):
            url = f"https://example.com/docs/p{i}"
            self.manager.mark_visited(url)
            
        # 5ページ訪問済みなので、次はFalseになるはず
        self.assertFalse(self.manager.can_crawl("https://example.com/docs/p6"))

    def test_add_discovered_url(self):
        # 有効な新規URL
        self.assertTrue(self.manager.add_discovered_url("https://example.com/docs/new"))
        
        # 既に発見済み
        self.assertFalse(self.manager.add_discovered_url("https://example.com/docs/new"))
        
        # 無効なURL
        self.assertFalse(self.manager.add_discovered_url("https://google.com"))

if __name__ == '__main__':
    unittest.main()
