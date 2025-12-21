import os
import re
import time
from typing import Optional

import requests

class ShopifyAPIError(Exception):
    """Base exception for Shopify API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class ShopifyConfigError(ShopifyAPIError):
    """Raised when required configuration is missing or invalid."""
    pass


class ShopifyNetworkError(ShopifyAPIError):
    """Raised when a network error occurs (connection, timeout, etc.)."""
    pass


class ShopifyRateLimitError(ShopifyAPIError):
    """Raised when rate limit is exceeded and all retries are exhausted."""
    pass


class ShopifyHTTPError(ShopifyAPIError):
    """Raised when an HTTP error response is received (4xx, 5xx)."""
    pass



def parse_link_header(link_header: Optional[str]) -> Optional[str]:
    """Parse Link header to extract next page URL."""
    if not link_header:
        return None
    
    # Match pattern: <URL>; rel="next"
    pattern = r'<([^>]+)>;\s*rel="next"'
    match = re.search(pattern, link_header)
    
    if match:
        return match.group(1)
    
    return None



def get_shopify_data(
    endpoint: str,
    params: Optional[dict] = None,
    store_url: Optional[str] = None,
    max_retries: int = 5,
    initial_backoff: float = 1.0
) -> dict:
    """Make a GET request to Shopify Admin REST API with pagination and retry logic."""
    # Get configuration from environment
    access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN')
    api_version = os.environ.get('SHOPIFY_API_VERSION')
    
    # Use provided store_url or fall back to environment variable
    shop_url = store_url or os.environ.get('SHOPIFY_SHOP_NAME')
    
    # Validate configuration
    if not access_token:
        raise ShopifyConfigError(
            "SHOPIFY_ACCESS_TOKEN environment variable is not set"
        )
    
    if not api_version:
        raise ShopifyConfigError(
            "SHOPIFY_API_VERSION environment variable is not set"
        )
    
    if not shop_url:
        raise ShopifyConfigError(
            "store_url parameter not provided and SHOPIFY_SHOP_NAME environment variable is not set"
        )
    
    # Normalize store URL (remove https:// if present)
    shop_url = shop_url.replace('https://', '').replace('http://', '').rstrip('/')
    
    # Build the full API URL
    # Format: https://{store}.myshopify.com/admin/api/{version}/{endpoint}
    base_url = f"https://{shop_url}/admin/api/{api_version}"
    
    # Ensure endpoint doesn't start with /
    endpoint = endpoint.lstrip('/')
    
    url = f"{base_url}/{endpoint}"
    
    # Set up headers
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Retry logic with exponential backoff for rate limiting
    backoff = initial_backoff
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30  # 30 second timeout
            )
            
            # Handle rate limiting (429)
            if response.status_code == 429:
                if attempt < max_retries:
                    # Get retry-after header if available
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            wait_time = backoff
                    else:
                        wait_time = backoff
                    
                    time.sleep(wait_time)
                    backoff *= 2  # Exponential backoff
                    continue
                else:
                    raise ShopifyRateLimitError(
                        f"Rate limit exceeded after {max_retries} retries",
                        status_code=429,
                        response_body=response.text
                    )
            
            # Handle other HTTP errors
            if response.status_code >= 400:
                raise ShopifyHTTPError(
                    f"HTTP {response.status_code}: {response.reason}",
                    status_code=response.status_code,
                    response_body=response.text
                )
            
            # Parse response
            data = response.json()
            
            # Extract pagination info from Link header
            link_header = response.headers.get('Link')
            next_page_url = parse_link_header(link_header)
            
            return {
                'data': data,
                'next_page_url': next_page_url
            }
            
        except requests.exceptions.Timeout as e:
            last_exception = e
            raise ShopifyNetworkError(
                f"Request timed out: {str(e)}"
            )
        except requests.exceptions.ConnectionError as e:
            last_exception = e
            raise ShopifyNetworkError(
                f"Connection error: {str(e)}"
            )
        except requests.exceptions.RequestException as e:
            last_exception = e
            raise ShopifyNetworkError(
                f"Network error: {str(e)}"
            )
    
    # Should not reach here, but just in case
    if last_exception:
        raise ShopifyNetworkError(f"Request failed: {str(last_exception)}")
    
    raise ShopifyAPIError("Unexpected error in get_shopify_data")


def get_all_shopify_data(
    endpoint: str,
    params: Optional[dict] = None,
    store_url: Optional[str] = None,
    max_pages: Optional[int] = None
) -> list:
    """Fetch all pages from a paginated Shopify endpoint."""
    results = []
    current_url = None
    page_count = 0
    
    while True:
        if max_pages and page_count >= max_pages:
            break
        
        if current_url:
            # For subsequent pages, use the full URL from Link header
            # We need to extract just the page_info parameter
            result = get_shopify_data(
                endpoint,
                params={'page_info': current_url.split('page_info=')[-1].split('&')[0]} if 'page_info=' in current_url else params,
                store_url=store_url
            )
        else:
            result = get_shopify_data(endpoint, params, store_url)
        
        results.append(result['data'])
        page_count += 1
        
        current_url = result['next_page_url']
        if not current_url:
            break
    
    return results
