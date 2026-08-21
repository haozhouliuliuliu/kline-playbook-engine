from __future__ import annotations

import base64
import io
import os
import secrets
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from PIL import Image, ImageDraw, ImageFont


def _split_env_list(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _transport_security_settings() -> TransportSecuritySettings:
    allowed_hosts = _split_env_list(os.getenv("MCP_ALLOWED_HOSTS"))
    allowed_origins = _split_env_list(os.getenv("MCP_ALLOWED_ORIGINS"))
    if not allowed_hosts and not allowed_origins:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


mcp = FastMCP(
    name="kline-chatgpt-vision-probe",
    stateless_http=True,
    transport_security=_transport_security_settings(),
)


TOOL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}


def _build_probe_png() -> bytes:
    """Create a blind runtime probe whose answer exists only in image pixels."""
    code = f"VIS-{secrets.token_hex(4).upper()}"
    line_kind = secrets.choice(["HORIZONTAL", "DIAGONAL_UP", "DIAGONAL_DOWN"])

    image = Image.new("RGB", (1280, 720), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=36)
    small_font = ImageFont.load_default(size=24)

    draw.text((70, 55), "CHATGPT MCP BLIND VISION PROBE", fill="black", font=font)
    draw.text((70, 145), f"CODE: {code}", fill="black", font=font)
    draw.text((70, 220), f"LINE: {line_kind}", fill="black", font=font)
    draw.text(
        (70, 300),
        "The CODE and LINE values are intentionally NOT returned as text by the MCP tool.",
        fill="black",
        font=small_font,
    )

    left, right = 120, 1160
    if line_kind == "HORIZONTAL":
        start, end = (left, 520), (right, 520)
    elif line_kind == "DIAGONAL_UP":
        start, end = (left, 600), (right, 400)
    else:
        start, end = (left, 400), (right, 600)
    draw.line([start, end], fill="black", width=12)
    draw.ellipse([start[0] - 12, start[1] - 12, start[0] + 12, start[1] + 12], fill="black")
    draw.ellipse([end[0] - 12, end[1] - 12, end[0] + 12, end[1] + 12], fill="black")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="vision_probe",
            title="Blind vision probe",
            description=(
                "Generate a fresh PNG containing a random CODE and LINE label. "
                "The answer is present only in the returned image pixels. "
                "Use this to test whether ChatGPT can actually consume MCP image content."
            ),
            inputSchema=TOOL_SCHEMA,
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
        )
    ]


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    if req.params.name != "vision_probe":
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text="Unknown tool")],
                isError=True,
            )
        )

    png = _build_probe_png()
    encoded = base64.b64encode(png).decode("ascii")

    # Deliberately return IMAGE CONTENT ONLY. No CODE/LINE text or metadata side channel.
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.ImageContent(
                    type="image",
                    data=encoded,
                    mimeType="image/png",
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
app = mcp.streamable_http_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
