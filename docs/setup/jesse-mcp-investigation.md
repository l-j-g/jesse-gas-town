# Jesse MCP Investigation

Date: 2026-06-02

## Summary

Updated 2026-06-02: MCP is working when run from a clean Jesse 2.2.2 project
root at `/Users/lg/gt/jesse_gas_town/crew/lg_mcp_project`.

The source fork at `/Users/lg/gt/jesse_gas_town/crew/lg` is still Jesse 1.13.11
and does not contain the MCP package. It remains useful for current repo work,
but it is not the MCP runtime.

## Startup Command

Working MCP runtime:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg_mcp_project
source .venv/bin/activate
jesse run
```

Persistent local session:

```bash
tmux new-session -d -s jesse-mcp -c /Users/lg/gt/jesse_gas_town/crew/lg_mcp_project \
  'source .venv/bin/activate && jesse run >>/tmp/jesse-mcp-project-run.log 2>&1'
```

Verified runtime:

- `127.0.0.1:9000`: Jesse dashboard/API.
- `127.0.0.1:9001`: Jesse Python Language Server websocket.
- `127.0.0.1:9002`: Jesse MCP Streamable HTTP server.
- `http://127.0.0.1:9002/mcp`: MCP handshake succeeds; `list_tools` returned 45 tools.
- Current persistent process runs in tmux session `jesse-mcp`.

## Source Evidence

Old local source inspected:

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

Upstream/current source inspected:

- `upstream/master:setup.py`: version `2.2.2`.
- `upstream/master:requirements.txt`: includes `mcp==1.26.0`.
- `upstream/master:jesse/cli.py`: calls `sync_agent_rules()` and
  `run_mcp_server(jesse_host=HOST, jesse_port=PORT)` during `jesse run`.
- `upstream/master:jesse/mcp/server.py`: starts `FastMCP` with
  `transport="streamable-http"`.
- `upstream/master:jesse/mcp/manager.py`: reads `MCP_PORT`, defaults to `9002`,
  requires `PASSWORD`, and starts `python -m jesse.mcp.server`.

## Codex Config

Codex has an MCP server entry:

```toml
[mcp_servers.jesse]
url = "http://localhost:9002/mcp"
```

The client config is correct for the working 2.2.2 runtime.

## Environment

The clean MCP project root contains:

- `.venv` with `jesse==2.2.2` and `mcp==1.26.0`.
- `.env` with `APP_PORT=9000`, `LSP_PORT=9001`, `MCP_PORT=9002`,
  `MCP_LOG_IN_TERMINAL=true`, and `PASSWORD=local-research-only`.
- `routes.py` copied from the baseline research project.
- `strategies` symlinked to `/Users/lg/gt/jesse_gas_town/crew/lg/strategies`.
- Jesse-generated `AGENTS.md` with managed rules for version `2.2.2`.

## Notes

Codex itself may need a restart or MCP settings refresh before the `jesse` tools
appear in the active tool list. The server side is verified and listening at the
configured URL.
