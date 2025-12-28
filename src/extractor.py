from bs4 import BeautifulSoup
import markdownify
import re

class ContentExtractor:
    """
    HTMLからコンテンツを抽出し、クリーンアップしてMarkdownに変換するクラス。
    """
    def __init__(self):
        pass

    def extract(self, html_content: str, source_url: str) -> str:
        """
        HTMLを解析し、ノイズを除去してMarkdownに変換します。
        冒頭にソースURLのヘッダーを追加します。
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # ノイズとなるタグを削除
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
            tag.decompose()

        # メインコンテンツの特定を試みる
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body', re.I))
        
        # 特定のメインコンテナが見つからない場合はbodyをフォールバックとして使用
        if not main_content:
            main_content = soup.body

        if not main_content:
            return f"Source URL: {source_url}\n\n(コンテンツが見つかりませんでした)"

        # Markdownに変換
        md = markdownify.markdownify(str(main_content), heading_style="ATX")

        # 過剰な改行を整理
        md = re.sub(r'\n{3,}', '\n\n', md).strip()

        return f"Source URL: {source_url}\n\n{md}\n\n---\n\n"
