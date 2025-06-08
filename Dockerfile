FROM python:3.9-slim

WORKDIR /app

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Miniconda環境用の依存関係をインストール
COPY environment.yml .
RUN pip install boto3 requests beautifulsoup4 feedparser schedule python-dateutil lxml

COPY . .

CMD ["python", "main.py"]