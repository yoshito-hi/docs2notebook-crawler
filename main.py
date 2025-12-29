import asyncio
import logging
import signal
import sys
from pathlib import Path
from urllib.parse import urlparse
from src.crawler import DocsCrawler

def signal_handler(sig, frame):
    print("\n中断されました。終了します。")
    sys.exit(0)

# SIGTSTP (Ctrl+Z) をハンドルして終了させる
signal.signal(signal.SIGTSTP, signal_handler)

def main():
    try:
        print("=== Docs2Notebook Crawler 設定 ===")
        print("各項目を設定してください（Enterでデフォルト値を使用）")
        
        # === 1. URL入力 (必須) ===
        target_url = ""
        while not target_url:
            target_url = input("\n[1/5] 対象URLを入力 (例: https://docs.python.org): ").strip()
            if not target_url:
                print("エラー: URLは必須です。")

        # === 2. 出力先ディレクトリ (デフォルト: Downloads) ===
        default_download_dir = Path.home() / "Downloads"
        user_output_dir = input(f"\n[2/5] 出力先ディレクトリを指定 [デフォルト: {default_download_dir}]: ").strip()
        
        if user_output_dir:
            output_dir_str = user_output_dir
        else:
            output_dir_str = str(default_download_dir)

        # === 3. 最大ページ数 (デフォルト: 20) ===
        max_pages = 20
        user_max_pages = input(f"\n[3/5] 最大クロールページ数 [デフォルト: {max_pages}]: ").strip()
        if user_max_pages:
            try:
                max_pages = int(user_max_pages)
            except ValueError:
                print(f"警告: 数値ではないため、デフォルト値({max_pages})を使用します。")

        # === 4. 並列リクエスト数 (デフォルト: 5) ===
        concurrency = 5
        user_concurrency = input(f"\n[4/5] 並列リクエストの最大数 [デフォルト: {concurrency}]: ").strip()
        if user_concurrency:
            try:
                concurrency = int(user_concurrency)
            except ValueError:
                print(f"警告: 数値ではないため、デフォルト値({concurrency})を使用します。")

        # === 5. 詳細ログ出力 (デフォルト: No) ===
        verbose = False
        user_verbose = input(f"\n[5/5] 詳細なログ出力を有効にしますか? (y/N) [デフォルト: No]: ").strip().lower()
        if user_verbose == 'y' or user_verbose == 'yes':
            verbose = True

        # ログ設定
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 自作モジュールのログレベルを設定
        if verbose:
            logging.getLogger("src").setLevel(logging.INFO)

        # 出力パスの構築
        output_dir = Path(output_dir_str).expanduser()
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"ディレクトリの作成に失敗しました: {e}")
                return

        # URLからファイル名を生成
        try:
            parsed = urlparse(target_url)
            domain = parsed.netloc.replace('.', '-')
            path = parsed.path.strip('/')
            
            if path:
                # パスがある場合は、ドメイン名_パス名.md（スラッシュはアンダースコアに置換）
                path_str = path.replace('/', '_')
                output_filename = f"{domain}_{path_str}.md"
            else:
                # ドメイン名のみの場合は、ドメイン名.md
                output_filename = f"{domain}.md"
                
            if not domain:
                output_filename = "merged_docs.md"
        except Exception:
            output_filename = "merged_docs.md"
        output_file_path = output_dir / output_filename
        
        # 設定確認表示
        print("\n" + "="*30)
        print(f"以下の設定で実行します:")
        print(f"  対象URL    : {target_url}")
        print(f"  出力先     : {output_file_path}")
        print(f"  最大ページ : {max_pages}")
        print(f"  並列数     : {concurrency}")
        print(f"  詳細ログ   : {'有効' if verbose else '無効'}")
        print("="*30 + "\n")

        # クローラーの初期化
        crawler = DocsCrawler(
            start_url=target_url, 
            output_file=str(output_file_path), 
            max_concurrent=concurrency,
            max_pages=max_pages
        )
        
        # 実行
        asyncio.run(crawler.run())
        
        print("完了！")
    except (KeyboardInterrupt, EOFError):
        print("\n中断されました。終了します。")
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()