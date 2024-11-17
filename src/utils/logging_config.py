import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from .config import config  # configインスタンスをインポート

def setup_logging():
    """ロギングの設定をセットアップ"""
    
    # ログディレクトリの作成
    log_dir = config.log_dir
    log_dir.mkdir(exist_ok=True)

    # ログファイル名の設定（日付付き）
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    # ロガーの基本設定
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # ファイルハンドラ（日別ローテーション）
            logging.handlers.TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            ),
            # コンソールハンドラ
            logging.StreamHandler()
        ]
    )

    # ルートロガーの取得
    logger = logging.getLogger()
    
    # デバッグモード時の追加設定
    if config.debug_mode:
        logger.setLevel(logging.DEBUG)
        # 既存のハンドラのレベルも変更
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    return logger

# メインロガーをセットアップ
logger = setup_logging()

__all__ = ['setup_logging', 'logger']