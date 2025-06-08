import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse


class WebMonitor:
    def __init__(self, db_manager, discord_notifier):
        self.db_manager = db_manager
        self.discord_notifier = discord_notifier
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def check_all_sites(self):
        """全サイトをチェック"""
        sites = self.db_manager.get_all_sites()
        print(f"Checking {len(sites)} sites at {datetime.now()}")

        for site in sites:
            try:
                self.check_site(site)
                time.sleep(2)  # 負荷軽減のため2秒待機
            except Exception as e:
                print(f"Error checking {site['site_name']}: {e}")

    def check_site(self, site):
        """個別サイトをチェック"""
        print(f"Checking: {site['site_name']}")

        # RSS優先でチェック
        if site.get('rss_url'):
            new_articles = self.check_rss(site)
        else:
            new_articles = self.check_website(site)

        # 新記事があればDiscordに通知
        for article in new_articles:
            self.notify_new_article(site, article)
            self.db_manager.add_article(
                site['site_id'],
                article['title'],
                article['url'],
                article.get('published_date')
            )

        # 最終チェック時刻更新
        self.db_manager.update_last_check(site['site_id'])

        print(f"Found {len(new_articles)} new articles from {site['site_name']}")

    def check_rss(self, site):
        """RSS/Atomフィードをチェック"""
        new_articles = []

        try:
            feed = feedparser.parse(site['rss_url'])

            for entry in feed.entries[:10]:  # 最新10件をチェック
                title = entry.get('title', 'No title')
                url = entry.get('link', '')
                published_date = entry.get('published', '')

                if self.db_manager.is_article_new(site['site_id'], title, url):
                    new_articles.append({
                        'title': title,
                        'url': url,
                        'published_date': published_date
                    })

        except Exception as e:
            print(f"RSS check error for {site['site_name']}: {e}")

        return new_articles

    def check_website(self, site):
        """Webサイトをクローリング"""
        new_articles = []

        try:
            response = self.session.get(site['url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 汎用的な記事リンクを探す
            article_links = self.extract_article_links(soup, site['url'])

            for link_data in article_links[:10]:  # 最新10件をチェック
                title = link_data['title']
                url = link_data['url']

                if self.db_manager.is_article_new(site['site_id'], title, url):
                    new_articles.append({
                        'title': title,
                        'url': url
                    })

        except Exception as e:
            print(f"Website check error for {site['site_name']}: {e}")

        return new_articles

    def extract_article_links(self, soup, base_url):
        """記事リンクを抽出"""
        links = []

        # 一般的な記事リンクのセレクタを試す
        selectors = [
            'a[href*="/article/"]',
            'a[href*="/news/"]',
            'a[href*="/post/"]',
            'a[href*="/blog/"]',
            'h1 a, h2 a, h3 a',
            '.article-title a',
            '.post-title a',
            '.entry-title a'
        ]

        found_links = set()

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href and href not in found_links:
                    full_url = urljoin(base_url, href)
                    title = element.get_text(strip=True)

                    if title and len(title) > 5:  # 短すぎるタイトルは除外
                        links.append({
                            'title': title,
                            'url': full_url
                        })
                        found_links.add(href)

        return links

    def notify_new_article(self, site, article):
        """新記事をDiscordに通知"""
        # ジャンル判定
        genre = self.determine_genre(article['title'], site.get('keywords', []))

        message = {
            'site_name': site['site_name'],
            'title': article['title'],
            'url': article['url'],
            'genre': genre
        }

        self.discord_notifier.send_notification(message)

    def determine_genre(self, title, keywords):
        """タイトルからジャンルを判定"""
        title_lower = title.lower()

        for keyword in keywords:
            if keyword.lower() in title_lower:
                return keyword

        # 基本的なキーワードマッチング
        if any(word in title_lower for word in ['tech', 'technology', 'ai', 'software']):
            return 'tech'
        elif any(word in title_lower for word in ['news', 'world', 'politics']):
            return 'news'
        elif any(word in title_lower for word in ['business', 'startup', 'finance']):
            return 'business'
        else:
            return 'general'