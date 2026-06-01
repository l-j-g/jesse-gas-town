# Jesse MCP Investigation

Date: 2026-06-02

## Summary

The local Jesse 1.13.11 checkout does not expose a working MCP endpoint from
`jesse run`. The configured Codex endpoint is `http://localhost:9002/mcp`, but
no process listens on port `9002` after startup.

## Startup Command

Run from the Jesse project root:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg
/Users/lg/src/jesse/.venv/bin/jesse run
```

Observed runtime:

- `127.0.0.1:9000`: Jesse FastAPI/web app, `GET /` returns `200`.
- `*:9001`: Jesse Python Language Server websocket, log says `LSP WS started at ws://localhost:9001/lsp`.
- `127.0.0.1:9002`: no listener; `curl http://127.0.0.1:9002/mcp` fails with connection refused.

## Source Evidence

Local source inspected:

- `jesse/cli.py`: `run()` validates cwd, runs migrations, installs/starts LSP,
  then runs one `uvicorn.run(fastapi_app, host=host, port=port, log_level="info")`.
  The app port defaults to `9000` via `APP_PORT`; no second MCP server/process is
  started.
- `jesse/services/lsp.py`: LSP default port is `9001`; it starts the downloaded
  Python Language Server, not MCP.
- `jesse/__init__.py`: registers FastAPI routers for websocket, backtest,
  optimization, candles, strategy, auth, config, system, file, LSP config, trades,
  orders, and tabs; no MCP router is registered.
- `setup.py` and `requirements.txt`: package version is `1.13.11`; requirements
  include `fastapi` and `uvicorn`, but no MCP server package.

Search result:

```bash
rg -n "\bmcp\b|MCP|9002|FastMCP|streamable|model context|Model Context" \
  /Users/lg/gt/jesse_gas_town/crew/lg/jesse \
  /Users/lg/src/jesse/jesse \
  -g '!static/**' -g '!**/static/**' -g '!**/__pycache__/**'
```

This found no runtime MCP implementation in the Jesse Python source.

## Codex Config

Codex has an MCP server entry:

```toml
[mcp_servers.jesse]
url = "http://localhost:9002/mcp"
```

The client config is present, but the server side is absent in this local Jesse
runtime.

## Blocker

MCP cannot be used yet for this project because Jesse 1.13.11 in this checkout
does not start or register a Streamable HTTP MCP server. Implementing a local
`/mcp` route here would be speculative and would not satisfy the requirement to
use Jesse's source-of-truth MCP tools.

Next action: find the separate Jesse MCP provider or upstream branch/release that
contains the actual MCP implementation, then wire Codex to that verified server.
Until then, use repo inspection plus local Jesse scripts/CLI as the fallback.
