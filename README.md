# Docs2Notebook Crawler

Docs2Notebook Crawler は、散らばったウェブドキュメントを一括でクロールし、ノイズを除去した上で1つの Markdown ファイルに統合するツールです。NotebookLM などの AI ツールに学習させるためのナレッジベース作成を自動化することを目的としています。

## 主な機能

-   **インテリジェント・クローリング**: 指定したルート URL から開始し、同一ドメイン内のリンクを自動的に探索します。
-   **SPA (Single Page Application) 対応**: Playwright を使用し、JavaScript の実行完了を待機してからコンテンツを取得するため、モダンなドキュメントサイトにも対応しています。
-   **コンテンツの浄化**: ヘッダー、フッター、ナビゲーション、スクリプトなどの「ノイズ」を除去し、メインコンテンツのみを抽出します。
-   **Markdown 変換**: 抽出した HTML を LLM が読みやすい Markdown 形式に変換します。
-   **ソース明記**: 各セクションの冒頭に `Source URL` を自動付与し、生成 AI が参照元を特定できるようにします。
-   **統合出力**: 全ページの内容を 1 つのファイル (`merged_docs.md`) にまとめて出力します。

## 技術スタック

-   **Language**: Python 3.10+
-   **Browser Engine**: Playwright (Chromium)
-   **HTML Parsing**: BeautifulSoup4
-   **Markdown Conversion**: markdownify
-   **Async Processing**: asyncio

## セットアップ

このプロジェクトでは Python のパッケージ管理に `uv` を推奨しています。

1.  **依存関係のインストール**:
    ```bash
    uv sync
    ```

2.  **ブラウザのインストール**:
    ```bash
    uv run playwright install chromium
    ```

## 使い方

以下のコマンドでクロールを開始します：

```bash
uv run python main.py [開始URL] --output [出力ファイル名]
```

### 例:
```bash
uv run python main.py https://docs.python.org/ja/3/tutorial/ --output python_tutorial.md
```

### オプション:
-   `url`: 開始するルート URL (必須)
-   `--output`, `-o`: 出力する Markdown ファイルのパス (デフォルト: `merged_docs.md`)
-   `--concurrency`, `-c`: 並列リクエストの最大数 (デフォルト: 5)
-   `--verbose`, `-v`: 詳細なログ出力を有効にします

## License
MIT
