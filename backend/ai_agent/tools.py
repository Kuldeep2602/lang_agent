import json
from typing import Optional

from langchain_core.tools import tool
from langchain_experimental.tools import PythonAstREPLTool

from shopify.client import get_shopify_data, get_all_shopify_data

# Limit items shown to LLM to reduce token usage
MAX_ITEMS_FOR_LLM = 10


@tool
def get_shopify_data_tool(
    endpoint: str,
    store_url: str,
    params: Optional[str] = None
) -> str:
    """
    Fetch data from the Shopify Admin REST API.
    
    Use this tool to retrieve orders, products, or customers from a Shopify store.
    
    Args:
        endpoint: The API endpoint. Must be one of:
            - 'orders.json' - Get orders (supports params: status, created_at_min, limit)
            - 'products.json' - Get products (supports params: status, limit)
            - 'customers.json' - Get customers (supports params: limit)
        store_url: The Shopify store URL (e.g., 'mystore.myshopify.com')
        params: Optional JSON string of query parameters (e.g., '{"limit": 50, "status": "any"}')
        
    Returns:
        JSON string containing the fetched data.
        
    Example:
        get_shopify_data_tool(endpoint='orders.json', store_url='mystore.myshopify.com', params='{"limit": 10}')
    """
    # Validate endpoint
    valid_endpoints = ['orders.json', 'products.json', 'customers.json']
    if endpoint not in valid_endpoints:
        return json.dumps({
            "error": f"Invalid endpoint '{endpoint}'. Must be one of: {valid_endpoints}"
        })
    
    # Parse params if provided
    parsed_params = None
    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Invalid params JSON: {str(e)}"
            })
    
    try:
        result = get_shopify_data(
            endpoint=endpoint,
            params=parsed_params,
            store_url=store_url
        )
        data = result['data']
        
        # Truncate large responses to reduce LLM token usage
        for key in list(data.keys()):
            if isinstance(data[key], list) and len(data[key]) > MAX_ITEMS_FOR_LLM:
                total_count = len(data[key])
                data[key] = data[key][:MAX_ITEMS_FOR_LLM]
                data[f'{key}_truncated'] = f"Showing {MAX_ITEMS_FOR_LLM} of {total_count} items"
        
        return json.dumps(data, default=str)
    except Exception as e:
        return json.dumps({
            "error": f"Shopify API error: {str(e)}"
        })


@tool
def get_all_shopify_data_tool(
    endpoint: str,
    store_url: str,
    params: Optional[str] = None,
    max_pages: int = 5
) -> str:
    """
    Fetch ALL pages of data from a paginated Shopify endpoint.
    
    Use this when you need complete data (e.g., all orders for analysis).
    Warning: This may take longer for large datasets.
    
    Args:
        endpoint: The API endpoint ('orders.json', 'products.json', 'customers.json')
        store_url: The Shopify store URL
        params: Optional JSON string of query parameters
        max_pages: Maximum number of pages to fetch (default: 5)
        
    Returns:
        JSON string containing all fetched data combined.
    """
    valid_endpoints = ['orders.json', 'products.json', 'customers.json']
    if endpoint not in valid_endpoints:
        return json.dumps({
            "error": f"Invalid endpoint '{endpoint}'. Must be one of: {valid_endpoints}"
        })
    
    parsed_params = None
    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Invalid params JSON: {str(e)}"
            })
    
    try:
        all_pages = get_all_shopify_data(
            endpoint=endpoint,
            params=parsed_params,
            store_url=store_url,
            max_pages=max_pages
        )
        
        # Combine all pages
        combined_data = {}
        for page in all_pages:
            for key, value in page.items():
                if key not in combined_data:
                    combined_data[key] = []
                if isinstance(value, list):
                    combined_data[key].extend(value)
                else:
                    combined_data[key] = value
        
        # Truncate for LLM but note total count
        for key in list(combined_data.keys()):
            if isinstance(combined_data[key], list) and len(combined_data[key]) > MAX_ITEMS_FOR_LLM:
                total_count = len(combined_data[key])
                combined_data[f'{key}_total_count'] = total_count
                combined_data[key] = combined_data[key][:MAX_ITEMS_FOR_LLM]
                combined_data[f'{key}_truncated'] = f"Showing {MAX_ITEMS_FOR_LLM} of {total_count} items. Use python_repl to analyze all data."
        
        return json.dumps(combined_data, default=str)
    except Exception as e:
        return json.dumps({
            "error": f"Shopify API error: {str(e)}"
        })



def create_python_repl_tool():
    """Create sandboxed Python REPL with pandas preloaded."""
    import pandas as pd
    
    # Create restricted globals with only safe operations
    safe_globals = {
        "pd": pd,
        "json": json,
        "__builtins__": {
            # Allow safe built-ins only
            "len": len,
            "range": range,
            "list": list,
            "dict": dict,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "round": round,
            "abs": abs,
            "print": print,
            "isinstance": isinstance,
            "type": type,
            "None": None,
            "True": True,
            "False": False,
        }
    }
    
    python_repl = PythonAstREPLTool(
        locals=safe_globals,
        name="python_repl",
        description="""
Execute Python code to analyze data. Pandas is available as 'pd'.

Use this tool for:
- Converting JSON data to DataFrames: pd.DataFrame(data)
- Aggregations: df.groupby('column').sum()
- Filtering: df[df['column'] > value]
- Sorting: df.sort_values('column', ascending=False)
- Statistics: df.describe(), df['column'].mean()

Always print your final result to see the output.
Return data as list of dicts for tables: df.to_dict('records')
"""
    )
    
    return python_repl


def get_all_tools():
    """Get all available tools for the agent."""
    return [
        get_shopify_data_tool,
        get_all_shopify_data_tool,
        create_python_repl_tool()
    ]
