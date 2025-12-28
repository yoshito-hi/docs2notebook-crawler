# Docker使用ガイド

## Dockerイメージのビルド

```bash
docker build -t docs2notebook-crawler .
```

## 基本的な使い方

### ヘルプの表示
```bash
docker run --rm docs2notebook-crawler
```

### ドキュメントのクロール
```bash
docker run --rm -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://docs.python.org/ja/3/tutorial/ \
  --output /app/output/python_tutorial.md
```

## オプション

- `url`: クロールを開始するルートURL（必須）
- `--output`, `-o`: 出力するMarkdownファイルのパス（デフォルト: `merged_docs.md`）
- `--concurrency`, `-c`: 並列リクエストの最大数（デフォルト: 5）
- `--max-pages`, `-m`: 最大クロールページ数（デフォルト: 20）
- `--verbose`, `-v`: 詳細なログ出力を有効化

## 使用例

### 基本的なクロール
```bash
docker run --rm -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://example.com/docs \
  --output /app/output/docs.md
```

### 詳細ログ付きで実行
```bash
docker run --rm -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://example.com/docs \
  --output /app/output/docs.md \
  --verbose
```

### 並列度とページ数を指定
```bash
docker run --rm -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://example.com/docs \
  --output /app/output/docs.md \
  --concurrency 10 \
  --max-pages 50
```

## 注意事項

- 出力ファイルを保存するには、`-v`オプションでボリュームマウントが必要です
- コンテナ内のパス（`/app/output/`）を指定してください
- ホスト側の`output`ディレクトリは事前に作成しておくことを推奨します

## トラブルシューティング

### 出力ファイルが見つからない場合
ボリュームマウントが正しく設定されているか確認してください：
```bash
mkdir -p output
docker run --rm -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://example.com --output /app/output/result.md
```

### メモリ不足エラーの場合
Dockerのメモリ制限を増やしてください：
```bash
docker run --rm -m 2g -v $(pwd)/output:/app/output docs2notebook-crawler \
  https://example.com --output /app/output/result.md
```
