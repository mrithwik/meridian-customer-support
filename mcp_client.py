import httpx
from config import MCP_SERVER_URL

# Stored after the handshake so every subsequent request is linked to our session
session_id = None

# Fix #1 — 406 Not Acceptable:
# MCP Streamable HTTP requires these headers on every request.
# Without them the server rejects the request because it doesn't know
# what response format we can handle.
BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def _get_headers() -> dict:
    # Fix #2 — TypeError: Header value must be str or bytes, not NoneType:
    # Some MCP servers don't return a session ID. We only include the header
    # when a session ID was actually returned, otherwise httpx raises a TypeError.
    headers = {**BASE_HEADERS}
    if session_id is not None:
        headers["mcp-session-id"] = session_id
    return headers


def initialize():
    """Perform the MCP handshake and store the session ID."""
    global session_id

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "meridian-chatbot", "version": "1.0.0"},
            "capabilities": {},
        },
    }

    response = httpx.post(MCP_SERVER_URL, json=payload, headers=BASE_HEADERS)
    response.raise_for_status()

    # The server may return a session ID in the headers to track our connection
    session_id = response.headers.get("mcp-session-id")

    # Complete the handshake with the initialized notification
    httpx.post(
        MCP_SERVER_URL,
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=_get_headers(),
    )


def list_tools():
    """Ask the MCP server what tools are available."""
    response = httpx.post(
        MCP_SERVER_URL,
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()["result"]["tools"]


def call_tool(tool_name: str, arguments: dict):
    """Call a specific tool on the MCP server and return the result."""
    response = httpx.post(
        MCP_SERVER_URL,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
        headers=_get_headers(),
    )
    response.raise_for_status()

    # Results come back as a list of content blocks — we extract the text
    content = response.json()["result"]["content"]
    return content[0]["text"] if content else "No result returned."
