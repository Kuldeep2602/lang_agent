# Shopify AI Agent

A fullstack AI application that intelligently analyzes Shopify store data (Orders, Products, Customers) using a LangChain ReAct agent with Google Gemini.


### Prerequisites
- Python 3.11+
- Node.js 18+
- Free Gemini API key from [Google AI Studio](https://aistudio.google.com)

# Backend Setup => 

cd backend
python -m venv venv
venv\Scripts\activate  
# macOS/Linux:
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Create .env file (copy from example)
cp .env.example .env
# Run migrations
python manage.py migrate
# Start the server
python manage.py runserver


## Frontend Setup =>
cd frontend
npm install
npm run dev
The app will be available at `http://localhost:5173`


## Agent Prompt

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

## Architecture

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


# Key Components

API Layer -> `backend/api/` 
AI Agent -> `backend/ai_agent/` 
Shopify Client -> `backend/shopify/` 
Frontend -> `frontend/src/` 

# Data Flow => 

1. User sends a query via the chat interface
2. Frontend posts to `POST /api/chat/` with `store_url` and `query`
3. Backend validates request and invokes the AI agent
4. Agent reasons about the query and calls appropriate tools
5. Tools fetch data from Shopify API and analyze with pandas
6. Agent returns structured JSON response (text, tables, charts)
7. Frontend renders the response with tables and optional charts

---

## Known Issues -> 
1. Rate Limiting
    - Gemini Free Tier: Limited to ~15 requests per minute. The agent handles quota errors gracefully but may fail on heavy usage.
    - If Query is too big not able to proceed , it throws error and as of december the capabilities 
    of Gemini free model has reduced significantly , not able to perform complex tasks

2. Agent Behavior
    - Complex multi-step queries may timeout on free Gemini tier
    - I was not able to test the chart generation gemini free tier is not supporting complex queries
    - Large datasets may cause timeout (120s limit)

3. Frontend
    - Charts require specific data format from agent (may not render for all queries)

4. Environment
    - `.env` file must be properly configured before starting



##  Questions & Answers (from Agent)

Q.  list 2 products ?

        Here are the top 2 products from your store based on a query for a limited list. The first product is a sample bar soap, and the second is a digital gift card.
        Product Details
        Title	ID	Status	Product Type
        (Sample) Coconut Bar Soap	7885649805405	active	—
        Gift Card	7885649969245	active	giftcard

Q.  what is the price of Coconut Bar Soap ?

        Based on the store data, the price for the product 'Coconut Bar Soap' is $0.00. Please note that this product is marked as a sample item.
        Product Price Details
        Product Title	Price
        (Sample) Coconut Bar Soap	$0.00

Q.  what is the price of Gift card ?

        The 'Gift Card' product on this Shopify store is available in several denominations, ranging from $10.00 to $100.00.
        Gift Card Denominations
        denomination	price
        $10	10.00
        $25	25.00
        $50	50.00
        $100	100.00

Q.  i want to buy  two $10 gift card of price 10?

        Based on the store's product data, the requested gift card is available. The store offers a 'Gift Card' product with a '$10' denomination option, priced at $10.00 each. The total cost for two $10 gift cards would be $20.00.
        Gift Card Product Details
        Product Name	Denomination	Price	Quantity Requested	Total Price
        Gift Card	$10	$10.00	2	$20.00

Q.  total how many gift cards in stock ?

        Based on the product inventory data for the store, the 'Gift Card' product currently has 0 units in stock across all available denominations ($10, $25, $50, and $100).
        Gift Card Stock Details
        Variant	Stock Quantity
        $10	0
        $25	0
        $50	0
        $100 0

Note -> If Query is too big not able to proceed , it throws error and as of december the capabilities 
of Gemini free model has reduced significantly , 

*** These are some of real questions & responses from the agent tested by me on Fronted

Frontend Url -> https://lang-agent-ajdr.vercel.app/





