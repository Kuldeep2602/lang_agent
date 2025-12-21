
import json
import logging
import concurrent.futures

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ai_agent.agent import run_agent
from shopify.client import (
    ShopifyAPIError,
    ShopifyRateLimitError,
    ShopifyNetworkError,
    ShopifyHTTPError,
)


MAX_REQUEST_SIZE_BYTES = 100 * 1024  # 100 KB
AGENT_TIMEOUT_SECONDS = 120  # Increased for free-tier model
logger = logging.getLogger(__name__)


def execute_with_timeout(func, *args, timeout=AGENT_TIMEOUT_SECONDS):
    """Execute a function with timeout."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        return future.result(timeout=timeout)


def create_response(text="", tables=None, chart_data=None):
    """Create standardized response dict."""
    return {
        "text": text if text is not None else "",
        "tables": tables if isinstance(tables, list) else [],
        "chart_data": chart_data if isinstance(chart_data, list) else [],
    }


def create_error_response(message, status_code):
    """Create JSON error response."""
    return JsonResponse(
        {"error": message, **create_response()},
        status=status_code
    )


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """POST /api/chat/ - Handle chat requests with store_url and query."""
    # Check request body size
    content_length = request.META.get('CONTENT_LENGTH')
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_SIZE_BYTES:
                return create_error_response(
                    "Request body too large. Maximum size is 100 KB.",
                    400
                )
        except (ValueError, TypeError):
            pass  # Let it proceed, will fail on JSON parse if invalid
    
    # Parse JSON body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return create_error_response("Invalid JSON format.", 400)
    
    # Validate required fields
    store_url = data.get("store_url")
    query = data.get("query")
    
    errors = []
    
    # Validate store_url
    if store_url is None:
        errors.append("'store_url' is required")
    elif not isinstance(store_url, str):
        errors.append("'store_url' must be a string")
    elif len(store_url.strip()) == 0:
        errors.append("'store_url' cannot be empty")
    
    # Validate query
    if query is None:
        errors.append("'query' is required")
    elif not isinstance(query, str):
        errors.append("'query' must be a string")
    elif len(query.strip()) == 0:
        errors.append("'query' cannot be empty")
    
    if errors:
        return JsonResponse(
            {"error": "Validation failed", "details": errors, **create_response()},
            status=400
        )
    
    # Initialize chat history (in-memory, per request)
    chat_history = []
    
    # Execute agent with timeout protection
    try:
        result = execute_with_timeout(
            run_agent,
            store_url.strip(),
            query.strip(),
            chat_history,
            timeout=AGENT_TIMEOUT_SECONDS
        )
        
        # Ensure response structure
        return JsonResponse(create_response(
            text=result.get("text", ""),
            tables=result.get("tables"),
            chart_data=result.get("chart_data")
        ))
        
    except concurrent.futures.TimeoutError:
        logger.warning("Agent execution timed out")
        return create_error_response(
            "Request timed out. Please try a simpler query.",
            504
        )
    
    except ShopifyRateLimitError:
        logger.warning("Shopify rate limit exceeded")
        return create_error_response(
            "Shopify API rate limit exceeded. Please try again later.",
            429
        )
    
    except (ShopifyAPIError, ShopifyHTTPError, ShopifyNetworkError) as e:
        logger.error("Shopify API error occurred")
        return create_error_response(
            "Unable to communicate with Shopify. Please try again.",
            502
        )
    
    except ValueError as e:
        # Validation errors from run_agent
        logger.warning("Agent validation error")
        return create_error_response(
            "Invalid request parameters.",
            400
        )
    
    except Exception as e:
        # Catch-all for LLM/agent errors
        logger.error("Agent execution failed")
        return create_error_response(
            "An error occurred while processing your request. Please try again.",
            500
        )
