import requests
import json
from datetime import datetime


class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_notification(self, message_data):
        """Discordに新記事通知を送信"""
        embed = {
            "title": f"🆕 {message_data['title']}",
            "url": message_data['url'],
            "color": self.get_color_for_genre(message_data['genre']),
            "fields": [
                {
                    "name": "サイト",
                    "value": message_data['site_name'],
                    "inline": True
                },
                {
                    "name": "ジャンル",
                    "value": f"#{message_data['genre']}",
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "Web Monitor Bot"
            }
        }

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print(f"Discord notification sent: {message_data['title']}")
        except requests.exceptions.RequestException as e:
            print(f"Discord notification failed: {e}")

    def get_color_for_genre(self, genre):
        """ジャンルに応じた色を返す"""
        colors = {
            'tech': 0x00D4AA,  # 緑
            'news': 0xFF6B6B,  # 赤
            'business': 0x4ECDC4,  # 青緑
            'general': 0x95A5A6  # グレー
        }
        return colors.get(genre.lower(), 0x95A5A6)

    def send_status_update(self, message):
        """ステータス更新を送信"""
        payload = {
            "content": f"ℹ️ {message}"
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Status update failed: {e}")