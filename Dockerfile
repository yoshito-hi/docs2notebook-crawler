# Python 3.12をベースイメージとして使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要な依存関係のインストール
# Playwrightのブラウザ実行に必要なライブラリを含む
RUN apt-get update && apt-get install -y \
  wget \
  gnupg \
  ca-certificates \
  fonts-liberation \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdbus-1-3 \
  libdrm2 \
  libgbm1 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libwayland-client0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxkbcommon0 \
  libxrandr2 \
  xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# uvのインストール
RUN pip install --no-cache-dir uv

# プロジェクトファイルをコピー
COPY pyproject.toml uv.lock* ./
COPY .python-version ./

# 依存関係のインストール
RUN uv sync --frozen

# Playwrightブラウザのインストール
RUN uv run playwright install chromium
RUN uv run playwright install-deps chromium

# アプリケーションコードをコピー
COPY main.py ./
COPY src/ ./src/

# エントリーポイントの設定
ENTRYPOINT ["uv", "run", "python", "main.py"]
