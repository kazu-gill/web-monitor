import boto3
import hashlib
from datetime import datetime
from botocore.exceptions import ClientError


class DatabaseManager:
    def __init__(self, dynamodb_endpoint=None):
        if dynamodb_endpoint:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_endpoint)
        else:
            self.dynamodb = boto3.resource('dynamodb')

        self.sites_table_name = 'WebMonitorSites'
        self.articles_table_name = 'WebMonitorArticles'

    def create_tables(self):
        """DynamoDBテーブルを作成"""
        try:
            # サイト管理テーブル
            self.dynamodb.create_table(
                TableName=self.sites_table_name,
                KeySchema=[
                    {'AttributeName': 'site_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'site_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"テーブル {self.sites_table_name} を作成しました")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                print(f"サイトテーブル作成エラー: {e}")

        try:
            # 記事履歴テーブル
            self.dynamodb.create_table(
                TableName=self.articles_table_name,
                KeySchema=[
                    {'AttributeName': 'site_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'article_hash', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'site_id', 'AttributeType': 'S'},
                    {'AttributeName': 'article_hash', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"テーブル {self.articles_table_name} を作成しました")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                print(f"記事テーブル作成エラー: {e}")

    def add_site(self, site_data):
        """監視サイトを追加"""
        table = self.dynamodb.Table(self.sites_table_name)
        site_data['last_check'] = ''

        try:
            table.put_item(
                Item=site_data,
                ConditionExpression='attribute_not_exists(site_id)'
            )
            print(f"サイト {site_data['site_name']} を追加しました")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                print(f"サイト追加エラー: {e}")

    def get_all_sites(self):
        """全監視サイトを取得"""
        table = self.dynamodb.Table(self.sites_table_name)
        response = table.scan()
        return response.get('Items', [])

    def update_last_check(self, site_id):
        """最終チェック時刻を更新"""
        table = self.dynamodb.Table(self.sites_table_name)
        table.update_item(
            Key={'site_id': site_id},
            UpdateExpression='SET last_check = :timestamp',
            ExpressionAttributeValues={':timestamp': datetime.now().isoformat()}
        )

    def is_article_new(self, site_id, title, url):
        """記事が新しいかチェック"""
        article_hash = hashlib.md5(f"{title}{url}".encode()).hexdigest()
        table = self.dynamodb.Table(self.articles_table_name)

        try:
            response = table.get_item(
                Key={'site_id': site_id, 'article_hash': article_hash}
            )
            return 'Item' not in response
        except ClientError:
            return True

    def add_article(self, site_id, title, url, published_date=None):
        """新しい記事を記録"""
        article_hash = hashlib.md5(f"{title}{url}".encode()).hexdigest()
        table = self.dynamodb.Table(self.articles_table_name)

        item = {
            'site_id': site_id,
            'article_hash': article_hash,
            'title': title,
            'url': url,
            'detected_date': datetime.now().isoformat()
        }

        if published_date:
            item['published_date'] = published_date

        table.put_item(Item=item)