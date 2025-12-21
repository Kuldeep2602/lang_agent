# Shopify AI Agent

A fullstack AI application that intelligently analyzes Shopify store data (Orders, Products, Customers) using a LangChain ReAct agent with Google Gemini.

![Architecture](https://img.shields.io/badge/Backend-Django-green) ![Frontend](https://img.shields.io/badge/Frontend-React-blue) ![AI](https://img.shields.io/badge/AI-LangChain-orange)

---

## 🚀 Setup Steps

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Shopify store with Admin API access
- Free Gemini API key from [Google AI Studio](https://aistudio.google.com)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp .env.example .env

# Edit .env with your credentials:
# - SHOPIFY_SHOP_NAME=your-store.myshopify.com
# - SHOPIFY_ACCESS_TOKEN=your-access-token
# - SHOPIFY_API_VERSION=2025-04
# - GEMINI_API_KEY=your-gemini-api-key

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

---

## 🤖 Agent Prompt

The AI agent uses a carefully crafted system prompt to guide its behavior:

```
You are a Shopify Data Analyst AI. Your role is to help users analyze their Shopify store data.

## Your Capabilities
You have access to the following tools:
1. **get_shopify_data_tool**: Fetch orders, products, or customers from Shopify
2. **get_all_shopify_data_tool**: Fetch ALL pages of data for comprehensive analysis
3. **python_repl**: Execute Python code for data analysis (pandas available as 'pd')

## How to Think Step-by-Step

1. **Understand the Query**: What data does the user need? What analysis do they want?

2. **Plan Your Approach**:
   - What Shopify endpoint(s) do I need? (orders.json, products.json, customers.json)
   - What parameters should I use? (limit, status, created_at_min, etc.)
   - What analysis will I perform?

3. **Fetch Data Only When Needed**:
   - Use get_shopify_data_tool for simple queries
   - Use get_all_shopify_data_tool only when you need complete data for aggregations

4. **Analyze with Python**:
   - Convert JSON to DataFrame: df = pd.DataFrame(json.loads(data))
   - Perform aggregations, filtering, sorting as needed
   - Always print results to see output

5. **Return Structured Output**:
   - Always format your final response as JSON with "text", "tables", and "chart_data" fields
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────────┐│
│  │ Chat UI  │  │ Table Render │  │ Chart Renderer (Recharts)  ││
│  └──────────┘  └──────────────┘  └─────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/chat/
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Django)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Layer (api/)                       │   │
│  │  • Request validation                                     │   │
│  │  • Timeout protection (120s)                              │   │
│  │  • Error handling (rate limits, network, validation)      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               AI Agent Layer (ai_agent/)                  │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │           LangGraph ReAct Agent                     │ │   │
│  │  │  • Google Gemini LLM                                │ │   │
│  │  │  • Step-by-step reasoning                           │ │   │
│  │  │  • Tool selection & execution                       │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                          │                                │   │
│  │           ┌──────────────┼──────────────┐                 │   │
│  │           ▼              ▼              ▼                 │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │   │
│  │  │ Shopify     │ │ Shopify     │ │ Python REPL │         │   │
│  │  │ Data Tool   │ │ All Data    │ │ (Pandas)    │         │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Shopify Client Layer (shopify/)              │   │
│  │  • GET-only requests                                      │   │
│  │  • Pagination handling (Link headers)                     │   │
│  │  • Rate limit handling (429 + exponential backoff)        │   │
│  │  • Retry logic                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Shopify Admin REST API                        │
│        GET /admin/api/{version}/{orders|products|customers}.json│
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| **API Layer** | `backend/api/` | Handles HTTP requests, validation, timeouts |
| **AI Agent** | `backend/ai_agent/` | LangChain ReAct agent with Gemini |
| **Shopify Client** | `backend/shopify/` | API client with pagination & rate limits |
| **Frontend** | `frontend/src/` | React chat interface with table/chart rendering |

### Data Flow

1. User sends a query via the chat interface
2. Frontend posts to `POST /api/chat/` with `store_url` and `query`
3. Backend validates request and invokes the AI agent
4. Agent reasons about the query and calls appropriate tools
5. Tools fetch data from Shopify API and analyze with pandas
6. Agent returns structured JSON response (text, tables, charts)
7. Frontend renders the response with tables and optional charts

---

## ⚠️ Known Issues

### Rate Limiting
- **Gemini Free Tier**: Limited to ~15-60 requests per minute. The agent handles quota errors gracefully but may fail on heavy usage.
- **Shopify API**: 429 errors are handled with exponential backoff (up to 5 retries).

### Data Limitations
- Only supports **GET** requests (read-only access)
- Maximum pagination depth of 5 pages by default
- Large datasets may cause timeout (120s limit)

### Agent Behavior
- Occasionally returns raw JSON instead of formatted text
- Complex multi-step queries may timeout on free Gemini tier
- Chart generation is optional and may not always be included

### Frontend
- Charts require specific data format from agent (may not render for all queries)
- No persistent chat history across page reloads
- Store URL must be manually entered in settings

### Environment
- Requires stable internet connection for both Shopify and Gemini APIs
- `.env` file must be properly configured before starting

---

## 📝 Sample Queries

```
"Show me my products"
"How many orders did we get in the last 7 days?"
"Which products are top sellers?"
"What cities generate the highest revenue?"
"List customers who ordered more than 3 times"
"What's my total revenue this month?"
```

---

## 📄 License

MIT License
