#config.py
import os
import configparser
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self, env='development'):
        self.env = env
        self.base_path = Path(__file__).parent.parent.parent
        self.config = self._load_config()
        self._load_secrets()
        self._setup_credentials()

    def _load_config(self):
        """設定ファイルの読み込み"""
        config = configparser.ConfigParser()
        config_path = self.base_path / 'config' / 'settings.ini'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                config.read_file(f)
        except UnicodeDecodeError:
            with open(config_path, 'r', encoding='cp932') as f:
                config.read_file(f)
                
        return config

    def _load_secrets(self):
        """環境変数ファイルの読み込み"""
        env_path = self.base_path / 'config' / 'secrets.env'
        if not env_path.exists():
            raise FileNotFoundError(f"Secrets file not found: {env_path}")
            
        load_dotenv(env_path, encoding='utf-8')

    def _setup_credentials(self):
        """認証情報ファイルのパスを設定"""
        credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_file:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in secrets.env")
            
        credentials_path = self.base_path / 'config' / credentials_file
        
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_path}\n"
                f"Expected file: {credentials_file}\n"
                f"Looking in: {self.base_path / 'config'}"
            )
            
        # 絶対パスを環境変数に設定
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path.absolute())

    @property
    def log_dir(self):
        """ログディレクトリのパスを取得"""
        log_dir = self.base_path / 'logs'
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    @property
    def credentials_path(self):
        return os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    @property
    def gsc_settings(self):
        return {
            'site_url': self.config['GSC']['SITE_URL'],
            'date_range': int(self.config['GSC']['DATE_RANGE']),
            'batch_size': int(self.config['GSC']['BATCH_SIZE']),
            'metrics': self.config['GSC']['METRICS'].split(','),
            'dimensions': self.config['GSC']['DIMENSIONS'].split(','),
            'retry_count': int(self.config['GSC']['RETRY_COUNT']),
            'retry_delay': int(self.config['GSC']['RETRY_DELAY'])
        }

    @property
    def debug_mode(self):
        return self.config[self.env].getboolean('DEBUG')

    @property
    def log_level(self):
        return self.config[self.env]['LOG_LEVEL']

    def __str__(self):
        return f"Config(env={self.env}, base_path={self.base_path})"

# グローバルインスタンスの作成
config = Config()