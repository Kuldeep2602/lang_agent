import json
import os
import re
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ai_agent.tools import get_all_tools
from ai_agent.prompts import SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE

def create_agent(model_name: str = "gemini-robotics-er-1.5-preview", temperature: float = 0.0):
    """Create the LangGraph ReAct agent with tools."""
    # Initialize the LLM with Gemini
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=os.environ.get("GEMINI_API_KEY")
    )
    
    # Get tools
    tools = get_all_tools()
    
    # Create the ReAct agent using LangGraph
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )
    
    return agent



def parse_agent_response(response: str) -> dict:
    """Parse agent response into structured format."""
    default_response = {
        "text": "",
        "tables": [],
        "chart_data": []
    }
    
    if not response:
        default_response["text"] = "No response generated."
        return default_response
    
    # Try to extract JSON from the response
    try:
        # First, try direct JSON parse
        parsed = json.loads(response)
        if isinstance(parsed, dict):
            return {
                "text": parsed.get("text", str(response)),
                "tables": parsed.get("tables", []),
                "chart_data": parsed.get("chart_data", [])
            }
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON block in markdown code fence
    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict):
                return {
                    "text": parsed.get("text", ""),
                    "tables": parsed.get("tables", []),
                    "chart_data": parsed.get("chart_data", [])
                }
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    json_match = re.search(r'\{[\s\S]*"text"[\s\S]*\}', response)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict):
                return {
                    "text": parsed.get("text", ""),
                    "tables": parsed.get("tables", []),
                    "chart_data": parsed.get("chart_data", [])
                }
        except json.JSONDecodeError:
            pass
    
    # Fallback: return response as text
    default_response["text"] = response
    return default_response


def convert_chat_history(chat_history: list) -> list:
    """Convert chat history to LangChain message format."""
    if not chat_history:
        return []
    
    messages = []
    for msg in chat_history:
        role = msg.get("role", "").lower()
        content = msg.get("content", "")
        
        if role == "user" or role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "assistant" or role == "ai":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    
    return messages


def extract_final_response(result: dict) -> str:
    """Extract final text response from LangGraph agent result."""
    messages = result.get("messages", [])
    
    # Get the last AI message (skip Human, Tool, and System messages)
    for msg in reversed(messages):
        # Check the message type using class name
        msg_type = type(msg).__name__
        
        # Only return content from AIMessage
        if msg_type == "AIMessage" and hasattr(msg, "content"):
            content = msg.content
            
            # Handle string content
            if isinstance(content, str) and content.strip():
                return content
            
            # Handle list content (Gemini returns list of parts)
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict):
                        # Extract text from dict (e.g., {"type": "text", "text": "..."})
                        if "text" in part:
                            text_parts.append(part["text"])
                if text_parts:
                    return "\n".join(text_parts)
    
    return ""



def run_agent(
    store_url: str,
    query: str,
    chat_history: Optional[list] = None
) -> dict:
    """Run the LangChain agent with a query. Returns dict with text, tables, chart_data."""
    # Validate inputs
    if not store_url:
        raise ValueError("store_url is required")
    
    if not query:
        raise ValueError("query is required")
    
    # Check for Gemini API key
    if not os.environ.get("GEMINI_API_KEY"):
        return {
            "text": "Error: GEMINI_API_KEY environment variable is not set. Get a free API key at https://aistudio.google.com",
            "tables": [],
            "chart_data": []
        }
    
    # Create the agent
    agent = create_agent()
    
    # Convert chat history to LangChain format
    lc_chat_history = convert_chat_history(chat_history)
    
    # Format the input with store URL
    formatted_input = HUMAN_PROMPT_TEMPLATE.format(
        store_url=store_url,
        query=query
    )
    
    # Build messages
    messages = lc_chat_history + [HumanMessage(content=formatted_input)]
    
    try:
        # Execute the agent with recursion limit to prevent runaway iterations
        result = agent.invoke(
            {"messages": messages},
            {"recursion_limit": 10}  # Limit reasoning loops to reduce API calls
        )
        
        # Extract the output
        output = extract_final_response(result)
        
        # Parse and return structured response
        return parse_agent_response(output)
        
    except Exception as e:
        # Parse error message to provide user-friendly response
        error_str = str(e)
        
        # Handle rate limit / quota errors
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            return {
                "text": "⚠️ API quota exceeded. Please wait a moment and try again, or upgrade your API plan.",
                "tables": [],
                "chart_data": []
            }
        
        # Handle model not found errors
        if "NOT_FOUND" in error_str or "404" in error_str:
            return {
                "text": "⚠️ AI model unavailable. Please try again later.",
                "tables": [],
                "chart_data": []
            }
        
        # Handle network/connection errors
        if "connection" in error_str.lower() or "timeout" in error_str.lower():
            return {
                "text": "⚠️ Connection error. Please check your internet and try again.",
                "tables": [],
                "chart_data": []
            }
        
        # Handle authentication errors
        if "PERMISSION_DENIED" in error_str or "401" in error_str or "403" in error_str:
            return {
                "text": "⚠️ API authentication failed. Please check your API key.",
                "tables": [],
                "chart_data": []
            }
        
        # Generic error (hide internal details)
        return {
            "text": "⚠️ Unable to process your request. Please try again or simplify your query.",
            "tables": [],
            "chart_data": []
        }
