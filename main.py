import argparse
import asyncio
import logging
from src.crawler import DocsCrawler

def main():
    parser = argparse.ArgumentParser(description="Docs2Notebook Crawler - ドキュメントをMarkdownに変換して統合")
    parser.add_argument("url", help="クロールを開始するルートURL")
    parser.add_argument("--output", "-o", default="merged_docs.md", help="出力するMarkdownファイルのパス")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="並列リクエストの最大数")
    parser.add_argument("--max-pages", "-m", type=int, default=20, help="最大クロールページ数")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細なログ出力を有効化")

    args = parser.parse_args()

    # ログ設定
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 自作モジュールのログレベルを設定
    if args.verbose:
        logging.getLogger("src").setLevel(logging.INFO)

    print(f"クロール開始: {args.url}")
    print(f"出力ファイル: {args.output}")

    # クローラーの初期化
    crawler = DocsCrawler(
        start_url=args.url, 
        output_file=args.output, 
        max_concurrent=args.concurrency,
        max_pages=args.max_pages
    )
    
    # 実行
    asyncio.run(crawler.run())
    
    print("完了！")

if __name__ == "__main__":
    main()