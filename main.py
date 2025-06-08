#!/usr/bin/env python3
import os
import time
import schedule
from datetime import datetime
from web_monitor import WebMonitor
from database import DatabaseManager
from discord_notifier import DiscordNotifier


def main():
    # 環境変数から設定を取得
    dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000')
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    if not discord_webhook_url:
        print("DISCORD_WEBHOOK_URL環境変数が設定されていません")
        return

    # 各コンポーネントの初期化
    db_manager = DatabaseManager(dynamodb_endpoint)
    discord_notifier = DiscordNotifier(discord_webhook_url)
    web_monitor = WebMonitor(db_manager, discord_notifier)

    # テーブル作成（初回のみ）
    db_manager.create_tables()

    # テストサイトを追加（初回のみ）
    test_sites = [
        {
            'site_id': 'test_site_1',
            'url': 'https://rss.cnn.com/rss/edition.rss',  # RSS有りのテスト
            'site_name': 'CNN RSS',
            'rss_url': 'https://rss.cnn.com/rss/edition.rss',
            'check_interval': 30,
            'keywords': ['news', 'world']
        },
        {
            'site_id': 'test_site_2',
            'url': 'https://news.ycombinator.com',  # クローリングのテスト
            'site_name': 'Hacker News',
            'rss_url': '',
            'check_interval': 60,
            'keywords': ['tech', 'startup']
        }
    ]

    for site in test_sites:
        db_manager.add_site(site)

    # スケジュール設定
    schedule.every(5).minutes.do(web_monitor.check_all_sites)

    print(f"Web Monitor started at {datetime.now()}")
    print("Press Ctrl+C to stop")

    # 初回実行
    web_monitor.check_all_sites()

    # スケジュール実行ループ
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoring stopped")


if __name__ == "__main__":
    main()