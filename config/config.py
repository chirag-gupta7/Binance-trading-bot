"""
Configuration module for Binance Futures Trading Bot
Loads API credentials from .env file
"""

import os
from dotenv import load_dotenv
from logger import get_logger

logger = get_logger()

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Get configuration
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')
BASE_URL = os.getenv('BINANCE_BASE_URL', 'https://fapi.binance.com')

# Validate configuration
def validate_config():
    """Validate that API credentials are configured"""
    if not API_KEY or not API_SECRET:
        logger.warning("API credentials not configured. Using test mode only.")
        return False
    
    if len(API_KEY) < 20 or len(API_SECRET) < 20:
        logger.error("API credentials appear invalid (too short)")
        return False
    
    logger.info("API credentials loaded successfully")
    return True

# Check configuration on import
HAS_API_CREDENTIALS = validate_config()
