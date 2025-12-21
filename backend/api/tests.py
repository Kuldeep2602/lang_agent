"""
Tests for Chat API endpoint.
"""

import json
from unittest.mock import patch, MagicMock
import concurrent.futures

from django.test import TestCase, Client


class ChatAPITestCase(TestCase):
    """Tests for POST /api/chat/ endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = '/api/chat/'
        self.valid_payload = {
            "store_url": "test.myshopify.com",
            "query": "Show me products"
        }
    
    # =========================================================================
    # Successful Requests
    # =========================================================================
    
    @patch('api.views.run_agent')
    def test_valid_request_returns_200(self, mock_run_agent):
        """Test that a valid POST request returns HTTP 200 with structured response."""
        mock_run_agent.return_value = {
            "text": "Here are your products",
            "tables": [{"title": "Products", "data": []}],
            "chart_data": []
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn('text', data)
        self.assertIn('tables', data)
        self.assertIn('chart_data', data)
        
        self.assertIsInstance(data['text'], str)
        self.assertIsInstance(data['tables'], list)
        self.assertIsInstance(data['chart_data'], list)
    
    @patch('api.views.run_agent')
    def test_agent_called_with_correct_params(self, mock_run_agent):
        """Test that run_agent is called with correct parameters."""
        mock_run_agent.return_value = {
            "text": "Response",
            "tables": [],
            "chart_data": []
        }
        
        self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        mock_run_agent.assert_called_once()
        args = mock_run_agent.call_args[0]
        
        self.assertEqual(args[0], "test.myshopify.com")
        self.assertEqual(args[1], "Show me products")
        self.assertEqual(args[2], [])  # Empty chat history
    
    # =========================================================================
    # Validation Errors (HTTP 400)
    # =========================================================================
    
    def test_missing_store_url_returns_400(self):
        """Test that missing store_url returns HTTP 400."""
        payload = {"query": "Show me products"}
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn("'store_url' is required", data.get('details', []))
    
    def test_missing_query_returns_400(self):
        """Test that missing query returns HTTP 400."""
        payload = {"store_url": "test.myshopify.com"}
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn("'query' is required", data.get('details', []))
    
    def test_empty_query_returns_400(self):
        """Test that empty query returns HTTP 400."""
        payload = {
            "store_url": "test.myshopify.com",
            "query": "   "
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn("'query' cannot be empty", data.get('details', []))
    
    def test_empty_store_url_returns_400(self):
        """Test that empty store_url returns HTTP 400."""
        payload = {
            "store_url": "",
            "query": "Show me products"
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_invalid_json_returns_400(self):
        """Test that invalid JSON returns HTTP 400."""
        response = self.client.post(
            self.url,
            data="not valid json",
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Invalid JSON', data['error'])
    
    def test_non_string_store_url_returns_400(self):
        """Test that non-string store_url returns HTTP 400."""
        payload = {
            "store_url": 123,
            "query": "Show me products"
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_non_string_query_returns_400(self):
        """Test that non-string query returns HTTP 400."""
        payload = {
            "store_url": "test.myshopify.com",
            "query": 123
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # =========================================================================
    # Method Not Allowed (HTTP 405)
    # =========================================================================
    
    def test_get_request_returns_405(self):
        """Test that GET request returns HTTP 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_put_request_returns_405(self):
        """Test that PUT request returns HTTP 405."""
        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_delete_request_returns_405(self):
        """Test that DELETE request returns HTTP 405."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)
    
    # =========================================================================
    # Error Handling
    # =========================================================================
    
    @patch('api.views.run_agent')
    def test_timeout_returns_504(self, mock_run_agent):
        """Test that timeout returns HTTP 504."""
        mock_run_agent.side_effect = concurrent.futures.TimeoutError()
        
        with patch('api.views.execute_with_timeout') as mock_timeout:
            mock_timeout.side_effect = concurrent.futures.TimeoutError()
            
            response = self.client.post(
                self.url,
                data=json.dumps(self.valid_payload),
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 504)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('timed out', data['error'].lower())
    
    @patch('api.views.execute_with_timeout')
    def test_shopify_rate_limit_returns_429(self, mock_execute):
        """Test that Shopify rate limit error returns HTTP 429."""
        from shopify.client import ShopifyRateLimitError
        mock_execute.side_effect = ShopifyRateLimitError("Rate limited")
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('api.views.execute_with_timeout')
    def test_shopify_api_error_returns_502(self, mock_execute):
        """Test that Shopify API error returns HTTP 502."""
        from shopify.client import ShopifyAPIError
        mock_execute.side_effect = ShopifyAPIError("API error")
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 502)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('api.views.execute_with_timeout')
    def test_generic_exception_returns_500(self, mock_execute):
        """Test that generic exception returns HTTP 500."""
        mock_execute.side_effect = Exception("Something went wrong")
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
        # Ensure no stack trace is exposed
        self.assertNotIn('Something went wrong', data['error'])
    
    # =========================================================================
    # Response Structure
    # =========================================================================
    
    @patch('api.views.run_agent')
    def test_response_always_has_required_keys(self, mock_run_agent):
        """Test that response always contains text, tables, and chart_data."""
        # Even with minimal return from agent
        mock_run_agent.return_value = {"text": "Hello"}
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        data = response.json()
        self.assertIn('text', data)
        self.assertIn('tables', data)
        self.assertIn('chart_data', data)
        
        # Ensure lists are returned, not None
        self.assertIsInstance(data['tables'], list)
        self.assertIsInstance(data['chart_data'], list)
    
    @patch('api.views.run_agent')
    def test_handles_none_values_from_agent(self, mock_run_agent):
        """Test that None values from agent are converted to defaults."""
        mock_run_agent.return_value = {
            "text": None,
            "tables": None,
            "chart_data": None
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        data = response.json()
        self.assertEqual(data['text'], "")
        self.assertEqual(data['tables'], [])
        self.assertEqual(data['chart_data'], [])
    
    def test_error_response_includes_response_structure(self):
        """Test that error responses include text, tables, and chart_data."""
        payload = {"store_url": "test.myshopify.com"}  # Missing query
        
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('text', data)
        self.assertIn('tables', data)
        self.assertIn('chart_data', data)
