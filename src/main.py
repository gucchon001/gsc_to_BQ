#main.py
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.config import Config
from src.utils.logging_config import logger
from src.modules.gsc_fetcher import GSCConnector

def main():
    try:
        # Initialize configuration
        logger.info("Initializing application...")
        config = Config(env=os.getenv('APP_ENV', 'development'))
        logger.info(f"Environment: {config.env}")
        
        # Insert test data into BigQuery
        logger.info("Inserting test data into BigQuery...")
        gsc = GSCConnector(config)
        gsc.insert_test_data()

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()