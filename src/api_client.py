"""
Binance API Client wrapper for Binance Futures Trading Bot
Handles API communication with proper error handling
"""

try:
    from binance.um_futures import UMFutures
    HAS_BINANCE_SDK = True
except ImportError:
    HAS_BINANCE_SDK = False

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import API_KEY, API_SECRET, BASE_URL, HAS_API_CREDENTIALS
from logger import get_logger

logger = get_logger()


class BinanceAPIClient:
    """Wrapper for Binance Futures API"""

    def __init__(self, testnet=False):
        """
        Initialize Binance API client
        
        Args:
            testnet: If True, use testnet (requires different credentials)
        """
        self.testnet = testnet
        self.client = None
        
        if not HAS_BINANCE_SDK:
            logger.warning("binance-connector not installed. Install with: pip install binance-connector")
            return
        
        if not HAS_API_CREDENTIALS:
            logger.warning("API credentials not configured. Using simulation mode only.")
            return
        
        try:
            self.client = UMFutures(
                key=API_KEY,
                secret=API_SECRET,
                base_url=BASE_URL if not testnet else 'https://testnet.binancefuture.com'
            )
            logger.info(f"Binance API client initialized ({'testnet' if testnet else 'mainnet'})")
        except Exception as e:
            logger.error(f"Failed to initialize Binance API client: {e}", exc_info=True)

    def is_connected(self) -> bool:
        """Check if API client is properly connected"""
        return self.client is not None

    def futures_create_order(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: float = None,
        price: float = None,
        **kwargs
    ) -> dict:
        """
        Create a futures order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            type: MARKET, LIMIT, STOP, TAKE_PROFIT, etc.
            quantity: Order quantity
            price: Limit price (if applicable)
            **kwargs: Additional parameters
            
        Returns:
            Order response
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
        }
        
        if quantity is not None:
            params['quantity'] = quantity
        
        if price is not None:
            params['price'] = price
        
        params.update(kwargs)
        
        logger.log_api_call('futures/order', 'POST', params)
        
        try:
            response = self.client.new_order(**params)
            logger.log_api_response('futures/order', 200, response)
            return response
        except Exception as e:
            logger.error(f"API error creating order: {e}", exc_info=True)
            raise

    def futures_cancel_order(self, symbol: str, orderId: int = None, origClientOrderId: str = None, **kwargs) -> dict:
        """
        Cancel a futures order
        
        Args:
            symbol: Trading pair
            orderId: Order ID to cancel
            origClientOrderId: Original client order ID
            **kwargs: Additional parameters
            
        Returns:
            Cancellation response
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        params = {'symbol': symbol}
        
        if orderId:
            params['orderId'] = orderId
        elif origClientOrderId:
            params['origClientOrderId'] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")
        
        params.update(kwargs)
        
        logger.log_api_call('futures/order', 'DELETE', params)
        
        try:
            response = self.client.cancel_order(**params)
            logger.log_api_response('futures/order', 200, response)
            return response
        except Exception as e:
            logger.error(f"API error cancelling order: {e}", exc_info=True)
            raise

    def futures_get_order(self, symbol: str, orderId: int = None, origClientOrderId: str = None, **kwargs) -> dict:
        """
        Get order details
        
        Args:
            symbol: Trading pair
            orderId: Order ID
            origClientOrderId: Original client order ID
            **kwargs: Additional parameters
            
        Returns:
            Order details
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        params = {'symbol': symbol}
        
        if orderId:
            params['orderId'] = orderId
        elif origClientOrderId:
            params['origClientOrderId'] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")
        
        params.update(kwargs)
        
        logger.log_api_call('futures/order', 'GET', params)
        
        try:
            response = self.client.query_order(**params)
            logger.log_api_response('futures/order', 200, response)
            return response
        except Exception as e:
            logger.error(f"API error fetching order: {e}", exc_info=True)
            raise

    def futures_get_open_orders(self, symbol: str = None, **kwargs) -> list:
        """
        Get all open orders
        
        Args:
            symbol: Optional trading pair to filter
            **kwargs: Additional parameters
            
        Returns:
            List of open orders
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        params = {}
        if symbol:
            params['symbol'] = symbol
        params.update(kwargs)
        
        logger.log_api_call('futures/openOrders', 'GET', params)
        
        try:
            response = self.client.get_open_orders(**params)
            logger.log_api_response('futures/openOrders', 200, response)
            return response
        except Exception as e:
            logger.error(f"API error fetching open orders: {e}", exc_info=True)
            raise

    def futures_account(self) -> dict:
        """
        Get account information
        
        Returns:
            Account details
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        logger.log_api_call('futures/account', 'GET')
        
        try:
            response = self.client.account()
            logger.log_api_response('futures/account', 200, response)
            return response
        except Exception as e:
            logger.error(f"API error fetching account: {e}", exc_info=True)
            raise

    def get_symbol_info(self, symbol: str) -> dict:
        """
        Get symbol trading rules
        
        Args:
            symbol: Trading pair
            
        Returns:
            Symbol information
        """
        if not self.client:
            raise Exception("API client not initialized")
        
        logger.debug(f"Fetching symbol info: {symbol}")
        
        try:
            response = self.client.exchange_info()
            for s in response.get('symbols', []):
                if s['symbol'] == symbol:
                    return s
            raise ValueError(f"Symbol {symbol} not found")
        except Exception as e:
            logger.error(f"API error fetching symbol info: {e}", exc_info=True)
            raise


# Global API client instance
_api_client = None


def get_api_client(testnet=False, force_new=False) -> BinanceAPIClient:
    """
    Get or create global API client instance
    
    Args:
        testnet: Use testnet
        force_new: Create new instance instead of using global
        
    Returns:
        API client instance
    """
    global _api_client
    
    if force_new:
        return BinanceAPIClient(testnet=testnet)
    
    if _api_client is None:
        _api_client = BinanceAPIClient(testnet=testnet)
    
    return _api_client
