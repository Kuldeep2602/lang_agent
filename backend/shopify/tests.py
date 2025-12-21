"""
Unit tests for Shopify API client.

Uses unittest.mock to mock HTTP responses for testing without real API calls.
"""

import os
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from shopify.client import (
    get_shopify_data,
    parse_link_header,
    ShopifyAPIError,
    ShopifyConfigError,
    ShopifyNetworkError,
    ShopifyRateLimitError,
    ShopifyHTTPError,
)


class TestParseLinkHeader(TestCase):
    """Tests for the Link header parsing function."""

    def test_parse_link_header_with_next(self):
        """Should extract next page URL from Link header."""
        link_header = '<https://store.myshopify.com/admin/api/2025-04/products.json?page_info=abc123>; rel="next"'
        result = parse_link_header(link_header)
        self.assertEqual(
            result,
            'https://store.myshopify.com/admin/api/2025-04/products.json?page_info=abc123'
        )

    def test_parse_link_header_with_previous_and_next(self):
        """Should extract next URL when both previous and next are present."""
        link_header = (
            '<https://store.myshopify.com/admin/api/2025-04/products.json?page_info=prev123>; rel="previous", '
            '<https://store.myshopify.com/admin/api/2025-04/products.json?page_info=next456>; rel="next"'
        )
        result = parse_link_header(link_header)
        self.assertEqual(
            result,
            'https://store.myshopify.com/admin/api/2025-04/products.json?page_info=next456'
        )

    def test_parse_link_header_only_previous(self):
        """Should return None when only previous link is present."""
        link_header = '<https://store.myshopify.com/admin/api/2025-04/products.json?page_info=abc>; rel="previous"'
        result = parse_link_header(link_header)
        self.assertIsNone(result)

    def test_parse_link_header_none(self):
        """Should return None when Link header is None."""
        result = parse_link_header(None)
        self.assertIsNone(result)

    def test_parse_link_header_empty(self):
        """Should return None when Link header is empty."""
        result = parse_link_header('')
        self.assertIsNone(result)


class TestGetShopifyData(TestCase):
    """Tests for the main get_shopify_data function."""

    def setUp(self):
        """Set up test environment variables."""
        self.env_patcher = patch.dict(os.environ, {
            'SHOPIFY_ACCESS_TOKEN': 'test_access_token',
            'SHOPIFY_API_VERSION': '2025-04',
            'SHOPIFY_SHOP_NAME': 'test-store.myshopify.com'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up environment variables."""
        self.env_patcher.stop()

    @patch('shopify.client.requests.get')
    def test_successful_get_request(self, mock_get):
        """Should return data for successful GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': [{'id': 1, 'title': 'Test Product'}]}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        result = get_shopify_data('products.json')

        self.assertEqual(result['data'], {'products': [{'id': 1, 'title': 'Test Product'}]})
        self.assertIsNone(result['next_page_url'])
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('test-store.myshopify.com', call_args[0][0])
        self.assertIn('2025-04', call_args[0][0])
        self.assertEqual(call_args[1]['headers']['X-Shopify-Access-Token'], 'test_access_token')

    @patch('shopify.client.requests.get')
    def test_successful_get_with_pagination(self, mock_get):
        """Should extract next page URL from Link header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': [{'id': 1}]}
        mock_response.headers = {
            'Link': '<https://test-store.myshopify.com/admin/api/2025-04/products.json?page_info=next123>; rel="next"'
        }
        mock_get.return_value = mock_response

        result = get_shopify_data('products.json')

        self.assertEqual(
            result['next_page_url'],
            'https://test-store.myshopify.com/admin/api/2025-04/products.json?page_info=next123'
        )

    @patch('shopify.client.requests.get')
    def test_get_with_custom_params(self, mock_get):
        """Should pass query parameters to the request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': []}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        get_shopify_data('products.json', params={'limit': 50, 'status': 'active'})

        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params'], {'limit': 50, 'status': 'active'})

    @patch('shopify.client.requests.get')
    def test_get_with_custom_store_url(self, mock_get):
        """Should use provided store_url instead of environment variable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': []}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        get_shopify_data('products.json', store_url='custom-store.myshopify.com')

        call_args = mock_get.call_args
        self.assertIn('custom-store.myshopify.com', call_args[0][0])

    @patch('shopify.client.requests.get')
    @patch('shopify.client.time.sleep')
    def test_rate_limit_retry_with_backoff(self, mock_sleep, mock_get):
        """Should retry with exponential backoff on 429 rate limit."""
        # First two calls return 429, third succeeds
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {}
        rate_limit_response.text = 'Rate limited'

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {'products': []}
        success_response.headers = {}

        mock_get.side_effect = [rate_limit_response, rate_limit_response, success_response]

        result = get_shopify_data('products.json', max_retries=5, initial_backoff=1.0)

        self.assertEqual(result['data'], {'products': []})
        self.assertEqual(mock_get.call_count, 3)
        # Verify exponential backoff: sleep(1.0), sleep(2.0)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)

    @patch('shopify.client.requests.get')
    @patch('shopify.client.time.sleep')
    def test_rate_limit_with_retry_after_header(self, mock_sleep, mock_get):
        """Should use Retry-After header value when present."""
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {'Retry-After': '5'}
        rate_limit_response.text = 'Rate limited'

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {'products': []}
        success_response.headers = {}

        mock_get.side_effect = [rate_limit_response, success_response]

        result = get_shopify_data('products.json')

        mock_sleep.assert_called_with(5.0)

    @patch('shopify.client.requests.get')
    @patch('shopify.client.time.sleep')
    def test_rate_limit_exhausted(self, mock_sleep, mock_get):
        """Should raise ShopifyRateLimitError after max retries."""
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {}
        rate_limit_response.text = 'Rate limited'
        mock_get.return_value = rate_limit_response

        with self.assertRaises(ShopifyRateLimitError) as context:
            get_shopify_data('products.json', max_retries=3)

        self.assertIn('Rate limit exceeded', str(context.exception))
        self.assertEqual(context.exception.status_code, 429)

    @patch('shopify.client.requests.get')
    def test_http_error_404(self, mock_get):
        """Should raise ShopifyHTTPError for 404 response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = 'Not Found'
        mock_response.text = '{"errors": "Not Found"}'
        mock_get.return_value = mock_response

        with self.assertRaises(ShopifyHTTPError) as context:
            get_shopify_data('nonexistent.json')

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn('404', str(context.exception))

    @patch('shopify.client.requests.get')
    def test_http_error_500(self, mock_get):
        """Should raise ShopifyHTTPError for 500 response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = 'Internal Server Error'
        mock_response.text = 'Server error'
        mock_get.return_value = mock_response

        with self.assertRaises(ShopifyHTTPError) as context:
            get_shopify_data('products.json')

        self.assertEqual(context.exception.status_code, 500)

    @patch('shopify.client.requests.get')
    def test_network_timeout_error(self, mock_get):
        """Should raise ShopifyNetworkError on timeout."""
        import requests as req
        mock_get.side_effect = req.exceptions.Timeout('Connection timed out')

        with self.assertRaises(ShopifyNetworkError) as context:
            get_shopify_data('products.json')

        self.assertIn('timed out', str(context.exception))

    @patch('shopify.client.requests.get')
    def test_network_connection_error(self, mock_get):
        """Should raise ShopifyNetworkError on connection failure."""
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError('Connection refused')

        with self.assertRaises(ShopifyNetworkError) as context:
            get_shopify_data('products.json')

        self.assertIn('Connection error', str(context.exception))


class TestShopifyConfigErrors(TestCase):
    """Tests for configuration validation."""

    def test_missing_access_token(self):
        """Should raise ShopifyConfigError when access token is missing."""
        with patch.dict(os.environ, {
            'SHOPIFY_API_VERSION': '2025-04',
            'SHOPIFY_SHOP_NAME': 'test-store.myshopify.com'
        }, clear=True):
            with self.assertRaises(ShopifyConfigError) as context:
                get_shopify_data('products.json')

            self.assertIn('SHOPIFY_ACCESS_TOKEN', str(context.exception))

    def test_missing_api_version(self):
        """Should raise ShopifyConfigError when API version is missing."""
        with patch.dict(os.environ, {
            'SHOPIFY_ACCESS_TOKEN': 'test_token',
            'SHOPIFY_SHOP_NAME': 'test-store.myshopify.com'
        }, clear=True):
            with self.assertRaises(ShopifyConfigError) as context:
                get_shopify_data('products.json')

            self.assertIn('SHOPIFY_API_VERSION', str(context.exception))

    def test_missing_store_url(self):
        """Should raise ShopifyConfigError when store URL is missing."""
        with patch.dict(os.environ, {
            'SHOPIFY_ACCESS_TOKEN': 'test_token',
            'SHOPIFY_API_VERSION': '2025-04'
        }, clear=True):
            with self.assertRaises(ShopifyConfigError) as context:
                get_shopify_data('products.json')

            self.assertIn('store_url', str(context.exception))

    def test_store_url_from_parameter(self):
        """Should use store_url parameter when env var is missing."""
        with patch.dict(os.environ, {
            'SHOPIFY_ACCESS_TOKEN': 'test_token',
            'SHOPIFY_API_VERSION': '2025-04'
        }, clear=True):
            with patch('shopify.client.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'products': []}
                mock_response.headers = {}
                mock_get.return_value = mock_response

                result = get_shopify_data('products.json', store_url='param-store.myshopify.com')

                call_args = mock_get.call_args
                self.assertIn('param-store.myshopify.com', call_args[0][0])


class TestURLNormalization(TestCase):
    """Tests for URL normalization in get_shopify_data."""

    def setUp(self):
        """Set up test environment variables."""
        self.env_patcher = patch.dict(os.environ, {
            'SHOPIFY_ACCESS_TOKEN': 'test_access_token',
            'SHOPIFY_API_VERSION': '2025-04',
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up environment variables."""
        self.env_patcher.stop()

    @patch('shopify.client.requests.get')
    def test_store_url_with_https(self, mock_get):
        """Should strip https:// from store URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': []}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        get_shopify_data('products.json', store_url='https://test-store.myshopify.com')

        call_url = mock_get.call_args[0][0]
        self.assertTrue(call_url.startswith('https://test-store.myshopify.com'))
        self.assertNotIn('https://https://', call_url)

    @patch('shopify.client.requests.get')
    def test_endpoint_with_leading_slash(self, mock_get):
        """Should handle endpoint with leading slash."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'products': []}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        get_shopify_data('/products.json', store_url='test-store.myshopify.com')

        call_url = mock_get.call_args[0][0]
        self.assertNotIn('//products', call_url)
        self.assertIn('/products.json', call_url)
