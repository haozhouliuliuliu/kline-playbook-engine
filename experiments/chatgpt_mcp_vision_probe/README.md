# ChatGPT MCP Blind Vision Probe

Status: `CANDIDATE / EXPERIMENT ONLY`

Purpose: test one question only — whether ChatGPT itself receives MCP `image` tool-result pixels as model-visible visual input.

This is deliberately **not** a Bilibili implementation yet. If this probe fails, building Bilibili enumeration/stream slicing behind the same ChatGPT MCP path would not satisfy the project requirement that ChatGPT itself perform the visual reasoning.

## Blindness property

Each `vision_probe` call generates a fresh random `CODE` and one of three random line types. Those values exist only inside the generated PNG. They are not returned as text, structured content, metadata, logs, or tool arguments.

Therefore the ChatGPT test prompt can be:

> Call `vision_probe`. Read the image itself and report exactly the `CODE:` value and the `LINE:` value. Do not infer or guess. If you cannot see the image pixels, say `VISION_NOT_AVAILABLE`.

PASS requires an exact match to both values visible in that invocation's PNG.

## Local run

```bash
cd experiments/chatgpt_mcp_vision_probe
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The Streamable HTTP MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

ChatGPT cannot connect directly to localhost. For a private/local server, use OpenAI Secure MCP Tunnel when available for the account/workspace, or a temporary HTTPS tunnel strictly for this probe. Do not expose project secrets or authenticated project data.

If using a hostname tunnel with MCP Python SDK DNS rebinding protection, set `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` before starting the server.

## Gate

- `PASS`: ChatGPT reports the exact runtime-random CODE and LINE. The next experiment may add Bilibili read-only frame extraction.
- `FAIL`: ChatGPT receives the tool call but cannot see the image pixels, or only a widget/user-visible image is rendered. Stop this route; do not build Bilibili ingestion behind it.
- `INCONCLUSIVE`: connector/tunnel cannot be established. Fix transport/entitlement only; do not interpret it as an image-path failure.

No production adoption, no `TOOL_REGISTRY` status change, and no `CURRENT_STATE` change is authorized by this experiment alone.
