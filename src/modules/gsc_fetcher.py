from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging
from src.utils.config import Config  # 絶対インポートに変更

class GSCConnector:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.bq_client = bigquery.Client()

        # 修正: 重複を避けて正しい形式で table_id を生成
        self.table_id = (
            f"{self.config.config['BIGQUERY']['PROJECT_ID']}"  # プロジェクトID
            f".{self.config.config['BIGQUERY']['DATASET_ID']}"  # データセット名
            f".{self.config.config['BIGQUERY']['TABLE_ID']}"   # テーブル名
        )

        # デバッグ用ログ
        self.logger.info(f"Constructed table_id: {self.table_id}")

    def insert_test_data(self):
        """BigQueryにテストデータを挿入する"""
        rows_to_insert = [
            {'page': '/example-page-1', 'clicks': 15, 'impressions': 150, 'ctr': 0.1, 'position': 5, 'date': '2024-11-18'},
            {'page': '/example-page-2', 'clicks': 25, 'impressions': 250, 'ctr': 0.1, 'position': 6, 'date': '2024-11-18'},
            {'page': '/example-page-3', 'clicks': 5, 'impressions': 50, 'ctr': 0.1, 'position': 10, 'date': '2024-11-18'}
        ]

        try:
            self.logger.info(f"Inserting {len(rows_to_insert)} rows into BigQuery table: {self.table_id}")
            errors = self.bq_client.insert_rows_json(self.table_id, rows_to_insert)
            if errors:
                self.logger.error(f"Failed to insert rows: {errors}")
            else:
                self.logger.info("Test data inserted successfully.")
        except Exception as e:
            self.logger.error(f"Error inserting test data: {e}", exc_info=True)

    def test_connection(self):
        """API接続テスト"""
        try:
            sites = self.service.sites().list().execute()
            return {
                'status': 'success',
                'sites': sites.get('siteEntry', [])
            }
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def fetch_and_insert_gsc_data(self):
        """Google Search Consoleデータを取得してBigQueryに挿入"""
        try:
            # 日付範囲の計算
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=self.config.gsc_settings['date_range'])

            # GSC APIクエリを構築
            request_body = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': self.config.gsc_settings['dimensions'],
                'rowLimit': self.config.gsc_settings['batch_size'],
            }

            self.logger.info(f"Fetching data from {start_date} to {end_date}...")
            response = self.service.searchanalytics().query(
                siteUrl=self.config.gsc_settings['site_url'],
                body=request_body
            ).execute()

            # データが存在しない場合
            if 'rows' not in response:
                self.logger.warning("No data returned from GSC API.")
                return

            # GSCデータをBigQuery形式に変換
            rows_to_insert = [
                {
                    'page': row['keys'][0],
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0.0),
                    'position': row.get('position', 0.0),
                    'date': start_date.strftime('%Y-%m-%d')  # 日付を追加
                }
                for row in response.get('rows', [])
            ]

            # データをBigQueryに挿入
            self._insert_to_bigquery(rows_to_insert)

        except HttpError as e:
            self.logger.error(f"HTTP Error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise

    def _insert_to_bigquery(self, rows):
        """BigQueryにデータを挿入する"""
        try:
            # WRITE_MODEの取得
            write_mode = self.config.config['BigQuery'].get('WRITE_MODE', 'APPEND').upper()

            # テーブル参照の構築
            table_ref = self.bq_client.dataset(
                self.config.config['BigQuery']['DATASET_ID']
            ).table(self.config.config['BigQuery']['TABLE_ID'])

            # データをロード
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND if write_mode == 'APPEND' else bigquery.WriteDisposition.WRITE_TRUNCATE
            )

            self.logger.info(f"Inserting {len(rows)} rows to BigQuery table: {self.table_id}")
            job = self.bq_client.load_table_from_json(rows, table_ref, job_config=job_config)
            job.result()  # ジョブ完了を待機

            self.logger.info("Data inserted successfully.")
        except Exception as e:
            self.logger.error(f"Error while inserting data to BigQuery: {e}")
            raise

def insert_test_data(self):
    """BigQueryにテストデータを挿入する"""
    rows_to_insert = [
        {'page': '/example-page-1', 'clicks': 15, 'impressions': 150, 'ctr': 0.1, 'position': 5, 'date': '2024-11-18'},
        {'page': '/example-page-2', 'clicks': 25, 'impressions': 250, 'ctr': 0.1, 'position': 6, 'date': '2024-11-18'},
        {'page': '/example-page-3', 'clicks': 5, 'impressions': 50, 'ctr': 0.1, 'position': 10, 'date': '2024-11-18'}
    ]

    try:
        self._insert_to_bigquery(rows_to_insert)
        self.logger.info("Test data inserted successfully.")
    except Exception as e:
        self.logger.error(f"Error inserting test data: {e}", exc_info=True)
