# Docs2Notebook Crawler

**Docs2Notebook Crawler** は、Web上の技術ドキュメント（特にSPAサイト）を効率的にクローリングし、AI（特にNotebookLMなど）が読みやすい単一のMarkdownファイルに統合するPython製ツールです。

## 📖 概要

新しい技術を学習する際、公式ドキュメントが多数のページに分散しており、全容を把握するのに時間がかかることがあります。また、それらをNotebookLMなどのAIツールに学習させるために、手動でコピー＆ペーストを行うのは非効率的です。

このツールは、指定したURLからドキュメントを自動的に収集し、ノイズ（広告やナビゲーション）を除去してMarkdown化、最終的に1つのファイルに結合します。これにより、「AIと対話しながら技術を理解する」ための準備を瞬時に完了させることができます。

## ✨ 特徴

*   **インテリジェント・クローリング**:
    *   指定されたルートURLから探索を開始し、同一ドメイン・同一パス配下のページを自動収集します。
    *   **SPA (Single Page Application) 完全対応**: Playwrightを使用し、JavaScriptのレンダリング完了を待機してからコンテンツを取得します。Headlessブラウザ（Chromium）を使用するため、動的なサイトも正確に取得可能です。
    *   **Scope Guard**: 指定ドメイン外へのリンクを自動的に除外し、無限クローリングを防止します。
*   **高品質なコンテンツ抽出**:
    *   `header`, `footer`, `nav`, `script` などのノイズを除去し、本文のみを抽出します。
    *   HTMLをLLMが理解しやすいMarkdown形式に変換します。
    *   各セクションの冒頭に `Source URL: ...` を自動付与するため、AIが回答する際の引用元が明確になります。
*   **単一ファイル出力**:
    *   全ページの内容を `merged_docs.md` (またはドメイン_パス名.md) に結合して出力します。NotebookLMへのアップロード作業が一回で済みます。

## 🛠 技術スタック

*   **Language**: Python 3.12+
*   **Core Logic**: Playwright (Browser Automation), asyncio (Async Processing)
*   **Parsing**: BeautifulSoup4, markdownify

## ⚙️ 前提条件

*   Python 3.12以上
*   pip (または uv などのパッケージマネージャ)

## 🚀 インストール

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/yoshito-hi/docs2notebook-crawler.git
    cd docs2notebook-crawler
    ```

2.  依存ライブラリをインストールします。
    ```bash
    pip install -r requirements.txt
    # または pyproject.toml を使用する場合 (例: uv)
    # uv sync
    ```
    ※ `requirements.txt` がない場合は直接以下を実行してください:
    ```bash
    pip install playwright beautifulsoup4 markdownify
    ```

3.  Playwrightのブラウザバイナリをインストールします。
    ```bash
    playwright install chromium
    ```

## 💻 使い方

`main.py` を実行すると、対話形式で設定を行えます。

```bash
python main.py
```

実行後、以下の項目を入力するよう促されます：

1.  **対象URL (必須)**: クロールを開始するトップページのURL (例: `https://docs.python.org/3/`)
2.  **出力先ディレクトリ**: 生成されたMarkdownファイルの保存先 (デフォルト: `~/Downloads`)
3.  **最大クロールページ数**: 取得するページの最大数 (デフォルト: `20`)
4.  **並列リクエスト数**: 同時にアクセスするブラウザ数 (デフォルト: `5`)

### 実行例

```text
=== 📝 Docs2Notebook Crawler 設定 ===
各項目を設定してください（Enterでデフォルト値を使用）

[1/4] 対象URLを入力 (例: https://docs.python.org): https://antigravity.google/docs

[2/4] 出力先ディレクトリを指定 [デフォルト: /Users/username/Downloads]: ./output

[3/4] 最大クロールページ数 [デフォルト: 20]: 50

[4/4] 並列リクエストの最大数 [デフォルト: 5]: 

... (クロール処理が実行されます) ...

🎉 完了しました！
```

### 結果の確認

指定した出力ディレクトリに Markdown ファイルが生成されます。
ファイル名はURLに基づいて自動生成されます（例: `antigravity-google_docs.md`）。
ドメインのみの場合は `domain-name.md`、取得できない場合は `merged_docs.md` となります。

## 🐳 Dockerでの実行

Dockerを使用して、環境構築の手間を省いて実行することも可能です。

### 1. イメージのビルド

```bash
docker build -t docs2notebook-crawler .
```

### 2. コンテナの実行

対話モード (`-it`) で実行し、出力ファイルをローカルに取り出すためにボリュームマウント (`-v`) を設定します。

```bash
docker run -it --rm \
  -v $(pwd)/output:/app/output \
  docs2notebook-crawler
```

**実行時の注意点:**
- アプリが起動したら、出力先ディレクトリの設定で **`/app/output`** (またはデフォルトの `./output` などを指定し、そこをマウント) を指定してください。
- 上記コマンドの例では、カレントディレクトリの `output` フォルダに結果が保存されます。

## 📂 ディレクトリ構成

```
.
├── main.py              # アプリケーションのエントリーポイント (CLI)
├── src/
│   ├── crawler.py       # Playwrightを使用したクローラーロジック
│   ├── extractor.py     # HTML解析・Markdown変換・クリーニングロジック
│   ├── url_manager.py   # URL管理・バリデーション・状態管理
│   └── logger.py        # ロギング設定
├── tests/
│   └── test_url_manager.py # 単体テスト
├── pyproject.toml       # プロジェクト設定・依存関係
├── 仕様書.md            # 設計仕様書
└── README.md            # 本ファイル
```
