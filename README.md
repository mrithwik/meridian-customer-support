---
title: Meridian Customer Support
emoji: 🏆
colorFrom: yellow
colorTo: blue
sdk: docker
pinned: false
license: mit
short_description: 'AI-powered chatbot to handle common support requests '
---

# Meridian Electronics — Customer Support Chatbot

An AI-powered customer support chatbot for Meridian Electronics, built using GPT-4o-mini and the Model Context Protocol (MCP). The chatbot connects to Meridian's internal business systems via an MCP server to handle real customer workflows.

---

## What It Does

Handles four core customer support workflows:

- **Browse products** — list, search, and get details on Meridian's product catalogue
- **Authenticate** — verify a customer's identity before accessing account data
- **Order history** — look up past orders for an authenticated customer
- **Place orders** — create new orders against Meridian's backend systems

---

## Architecture

```
Customer (Browser)
      │
      ▼
  Gradio UI
      │
      ▼
  Python Backend (app.py)
      │
      ├── GPT-4o-mini (OpenAI)
      │   Tool calling + agent loop
      │
      └── MCP Client (mcp_client.py)
              │  Streamable HTTP
              ▼
         MCP Server (GCP Cloud Run)
              │
              ▼
         Meridian's Business Systems
         (products, orders, customers)
```

### Files

| File | Responsibility |
|------|---------------|
| `config.py` | Loads environment variables |
| `mcp_client.py` | MCP handshake, tool discovery, tool execution |
| `app.py` | Agent loop + Gradio chat interface |
| `Dockerfile` | Container config for HF Spaces deployment |

---

## How the Agent Loop Works

1. App starts → connects to MCP server → fetches all available tools
2. Customer sends a message
3. GPT-4o-mini receives the message + tool list
4. GPT decides to respond directly or call a tool
5. If tool call → `mcp_client.py` executes it → result fed back to GPT
6. GPT forms the final natural language response
7. Loop repeats until GPT stops calling tools

---

## MCP Tools

The chatbot discovers these tools automatically from the MCP server at startup:

| Tool | What it does |
|------|-------------|
| `list_products` | Browse all products |
| `get_product` | Get details on a specific product |
| `search_products` | Search by keyword |
| `get_customer` | Look up a customer account |
| `verify_customer_pin` | Authenticate a customer |
| `list_orders` | View order history |
| `get_order` | Get details on a specific order |
| `create_order` | Place a new order |

---

## Setup & Running Locally

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

### Steps

```bash
# Clone the repo
git clone https://github.com/mrithwik/Meridian-customer-support
cd Meridian-customer-support

# Create environment file
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Install dependencies and run
uv run app.py
```

Open [http://localhost:7860](http://localhost:7860) in your browser.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `MCP_SERVER_URL` | No | MCP server endpoint (defaults to Meridian's server) |

---

## Security

- LLM restricted to customer support topics only — off-topic requests refused
- System prompt blocks prompt injection attempts
- Customer PINs never echoed back in responses
- MCP sessions reinitialised per conversation to prevent data leaking between users
- **Note for production:** Customer data currently passes through OpenAI's API. A data processing agreement or private model deployment is required before going live.

---

## Known Limitations

1. **No frontend authentication** — customers identify via email and PIN in chat. Production requires a proper login flow before the chatbot loads.
2. **OpenAI data privacy** — customer data passes through OpenAI's servers. Needs a DPA or private model for production.
3. **No streaming** — this version of Gradio's ChatInterface doesn't support streaming responses. Fixable with a Gradio upgrade or Next.js frontend.

---

## Production Roadmap

| Layer | Current | Production |
|-------|---------|-----------|
| Frontend | Gradio | Next.js (Vercel) |
| Backend | Gradio built-in | FastAPI (App Runner / Cloud Run) |
| LLM | OpenAI API | Azure OpenAI or AWS Bedrock (private) |
| Auth | PIN in chat | OAuth / login page |
| Sessions | Per conversation | Per user, server-side |
| Logging | print() | Structured logs + Langfuse |
| Deployment | HF Spaces | Vercel + App Runner + GitHub Actions |

---

## Tech Stack

- **Python 3.12**
- **OpenAI SDK** — GPT-4o-mini with tool calling
- **Gradio** — chat interface
- **httpx** — HTTP client for MCP communication
- **python-dotenv** — environment variable management
- **Docker** — containerisation for HF Spaces
