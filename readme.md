# Web Monitor Bot

WebサイトやRSSフィードの更新を監視し、新記事をDiscordに自動通知するシステムです。

## 機能

- 📡 RSS/Atomフィード監視
- 🕷️ Webクローリング（RSS非対応サイト）
- 🎯 ジャンル自動判定
- 📨 Discord通知（Webhook）
- 🗄️ DynamoDB記事履歴管理
- ⏰ 定期実行スケジューリング

## アーキテクチャ

### ローカル開発環境
- Python 3.9 + Miniconda
- DynamoDB Local（Docker）
- Discord Webhook

### AWS本番環境（予定）
- Lambda（監視処理）
- DynamoDB（データ保存）
- EventBridge（スケジューリング）
- Parameter Store（機密情報）

## セットアップ

### 1. リポジトリクローン
```bash
git clone <repository-url>
cd web-monitor
```

### 2. Conda環境構築
```bash
conda env create -f environment.yml
conda activate web-monitor
```

### 3. Discord Webhook設定
1. Discordサーバー設定 → 連携サービス → ウェブフック
2. 新しいウェブフック作成
3. `.env`ファイル作成:
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 4. 実行

#### 簡単テスト（推奨）
```bash
conda activate web-monitor
export DISCORD_WEBHOOK_URL='your_webhook_url'
python local_dev.py
```

#### フル環境テスト
```bash
docker-compose up -d
docker-compose logs -f web-monitor
```

## ファイル構成

```
web-monitor/
├── main.py              # メインアプリケーション
├── local_dev.py         # ローカル開発用
├── web_monitor.py       # 監視ロジック
├── database.py          # DynamoDB操作
├── discord_notifier.py  # Discord通知
├── environment.yml      # Conda環境定義
├── docker-compose.yml   # Docker設定
├── Dockerfile
├── .env                 # 環境変数（要作成）
├── .gitignore
└── README.md
```

## 監視サイト設定

### RSS対応サイト
```python
{
    'site_id': 'cnn_rss',
    'url': 'https://rss.cnn.com/rss/edition.rss',
    'site_name': 'CNN RSS',
    'rss_url': 'https://rss.cnn.com/rss/edition.rss',
    'check_interval': 30,
    'keywords': ['news', 'world']
}
```

### クローリング対象サイト
```python
{
    'site_id': 'hackernews',
    'url': 'https://news.ycombinator.com',
    'site_name': 'Hacker News',
    'rss_url': '',  # 空の場合はクローリング
    'check_interval': 60,
    'keywords': ['tech', 'startup']
}
```

## カスタマイズ

### ジャンル判定ロジック
`web_monitor.py`の`determine_genre()`メソッドを編集

### クローリング対象要素
`web_monitor.py`の`extract_article_links()`メソッドのセレクタを調整

### Discord通知フォーマット
`discord_notifier.py`の`send_notification()`メソッドを編集

## AWS展開

### Lambda用調整項目
- [ ] `schedule`ライブラリ → EventBridge
- [ ] 環境変数 → Parameter Store
- [ ] ログ出力 → CloudWatch
- [ ] デプロイパッケージ作成

### インフラ構築
- [ ] DynamoDB テーブル作成
- [ ] Lambda 関数デプロイ
- [ ] EventBridge ルール設定
- [ ] IAM ロール・ポリシー

## トラブルシューティング

### Discord通知が届かない
- Webhook URLを確認
- チャンネル権限を確認

### クローリングが失敗する
- サイト固有のセレクタ調整が必要
- `User-Agent`ヘッダーの調整

### DynamoDB接続エラー
- Docker コンテナが起動しているか確認
- エンドポイントURLが正しいか確認

## コスト見積もり（AWS）

- Lambda: 数百円/月
- DynamoDB: 1,000-3,000円/月
- その他: 数百円/月

**合計: 2,000-5,000円/月程度**

## Setup Environment
# Web Monitor ローカル検証環境セットアップ

## 1. ディレクトリ構成
```
web-monitor/
├── docker-compose.yml
├── Dockerfile
├── environment.yml     # Conda環境定義
├── main.py
├── database.py
├── web_monitor.py
├── discord_notifier.py
├── .env
└── data/              # DynamoDB Local用データ
```

## 2. Discord Webhook URL取得
1. Discordサーバーの設定 → 連携サービス → ウェブフック
2. 新しいウェブフックを作成
3. WebhookURLをコピー

## 3. 環境変数設定
`.env`ファイルを作成：
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

## ローカル開発環境（Miniconda）
```bash
# Conda環境作成
conda env create -f environment.yml

# 環境アクティベート
conda activate web-monitor

# ローカル実行（Docker使わない場合）
# DynamoDB Localを別途起動してから
python main.py
```

## 4. 実行（Docker使用）
```bash
# プロジェクトディレクトリ作成
mkdir web-monitor && cd web-monitor

# 全ファイルを配置後
docker-compose up -d

# ログ確認
docker-compose logs -f web-monitor
```

## 5. 動作確認
- DynamoDBテーブルが作成される
- テストサイト（CNN RSS、Hacker News）が追加される
- 5分ごとに新記事をチェック
- 新記事があればDiscordに通知

## 6. 手動テスト
```bash
# コンテナに入る
docker-compose exec web-monitor bash

# 手動で一度だけ実行
python -c "from web_monitor import WebMonitor; from database import DatabaseManager; from discord_notifier import DiscordNotifier; import os; db=DatabaseManager(os.getenv('DYNAMODB_ENDPOINT')); discord=DiscordNotifier(os.getenv('DISCORD_WEBHOOK_URL')); monitor=WebMonitor(db, discord); monitor.check_all_sites()"
```

## 7. カスタマイズポイント
- `main.py`のtest_sitesで監視サイトを追加
- `web_monitor.py`のextract_article_linksでクローリングロジック調整
- `discord_notifier.py`で通知フォーマット変更

## トラブルシューティング
- DynamoDB接続エラー: コンテナ起動順序を確認
- Discord通知失敗: Webhook URLを確認
- クローリング失敗: サイト固有のセレクタ調整が必要


## ライセンス
MIT License
## 貢献
Issue・Pull Request歓迎です。
