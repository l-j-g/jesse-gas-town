# Jesse Repository Guide for AI Agents

## Overview
The jesse repository is the **core open-source framework** of the Jesse trading system. It contains the main Python codebase for backtesting trading strategies, importing historical data from crypto exchanges, running optimizations, and providing the API backend for the dashboard. It glues together the other repositories and makes them work together.

## Key Characteristics

### Central Framework
- **jesse-live depends on this** - Changes here affect live trading
- **jesse-rust integrates here** - Rust functions are called from this codebase
- **dashboard consumes this API** - Frontend uses the FastAPI routes and controller files. 

### Technology Stack
- **Python** - Primary language
- **FastAPI** - API framework for all routes
- **NumPy** - Array operations and calculations
- **keewee** - ORM for the database

## Development Workflow

### Making Changes
When implementing features or fixing bugs:

1. **Understand the scope** - Determine if other repositories such as the dashboard need updates
2. **Implement the code** in the appropriate module
3. **Write/update tests** - Maintain test coverage
4. **Run tests** to verify changes:
   ```bash
   cd /Users/lg/src/jesse
   ./scripts/run-local-pytest.sh
   ```
5. **Consider jesse-live** - Does this affect live trading?
6. **Update API routes** if needed - Follow FastAPI patterns
7. **Don't restart server** unless specifically asked

### Python Environment
Use the repo-local Jesse interpreter after bootstrapping:
```
/Users/lg/src/jesse/.venv/bin/python
```

Bootstrap it once from the repo root:
```bash
cd /Users/lg/src/jesse
./scripts/setup-local-codex-env.sh
```

The bootstrap script uses `/opt/homebrew/Caskroom/miniconda/base/bin/python` (Python 3.12) to create `.venv`, installs dependencies from `requirements.txt`, and installs Jesse in editable mode.

### Running Jesse Backend
The API server provides routes for the dashboard:
```bash
# Stop any running process
pkill -f "jesse run"

# Start Jesse from bot directory (not jesse/)
cd /path/to/your/bot
/Users/lg/src/jesse/.venv/bin/jesse run > /tmp/jesse-output.log 2>&1 &

# Server runs at http://localhost:9001

# Check logs
tail -f /tmp/jesse-output.log
```

**Important**: Don't restart Jesse after code changes unless explicitly requested.

### Running Tests
Run the test suite after changes if asked.
```bash
cd /Users/lg/src/jesse
./scripts/run-local-pytest.sh
```

Run the Jesse strategy baseline suite when working on strategy semantics, order handling, evaluation helpers, or framework-level trading behavior:
```bash
cd /Users/lg/src/jesse
./scripts/run-jesse-strategy-suite.sh
```

If you've updated jesse-rust, run tests after building:
```bash
cd /path/to/your/jesse-rust
./build-local.sh

cd /Users/lg/src/jesse
./scripts/run-local-pytest.sh
```

## Important Notes

### Debugging
- **Use `jh.debug()` for all debugging output** - Never use plain `print()`
- **Log format**: `[2024-12-06 18:23:12] ==> Your message here`
- Logs include timestamps and `==>` prefix
- Essential for debugging backtests and live trading sessions

### API Routes
- **Default to POST endpoints** unless specifically asked for GET
- Use FastAPI decorators and patterns
- Follow the structure of existing routes in `jesse/routes/`
- Return proper HTTP status codes and JSON responses
- Handle errors gracefully

### Code Style
- Don't write comments for functions unless asked
- Never try to install new packages - assume they're already installed. if need to install new packages, ask me first.
- Follow existing patterns and conventions
- Maintain consistency with the current codebase
- Try to import only at the top of the file.

### Strategy Development With Codex
- Start Codex from the repo root with the Jesse profile:
  ```bash
  codex -C /Users/lg/src/jesse --profile jesse
  ```
- For Gas Town strategy orchestration, read `docs/gas-town-strategy-lab.md` and `docs/gas-town-prompts.md`.
- Use the `jesse-gas-town-strategy-lab` skill when generating strategy ideas, dispatching Gas Town workers, evaluating candidates, or paper-gating strategy candidates.
- Read `docs/jesse-strategy-playbook.md` for the intended `Strategy` lifecycle and trade-placement contract.
- Read `docs/jesse-strategy-evaluation.md` before evaluating, reviewing, or optimizing a strategy.
- When designing a new strategy, start from an explicit market edge and regime thesis, then translate it into Jesse-native lifecycle methods and order semantics.
- Default to crypto futures strategy assumptions unless the user specifies a different market.
- Start from a concrete archetype such as trend pullback, breakout, range mean reversion, or exhaustion reversal before selecting indicators.
- Before changing strategy logic, inspect `jesse/strategies/Strategy.py`, `jesse/indicators/__init__.py`, `jesse/helpers.py`, `jesse/testing_utils.py`, and the relevant tests in `tests/`.
- Prefer built-in Jesse indicators, helpers, sizing utilities, and strategy lifecycle hooks over custom abstractions.
- Optimize for profit with robustness constraints. Do not treat raw backtest profit as sufficient if drawdown, trade quality, or parameter sensitivity are weak.
- Prefer simpler strategies that beat a strong baseline over elaborate indicator stacks with weak interpretability.
- For optimization or backtest changes, inspect `jesse/config.py` and the relevant files under `jesse/modes/` before changing hyperparameters or execution flow.
- Use targeted `pytest` coverage first, then run broader tests only when the change warrants it.
- Use `./scripts/run-local-pytest.sh` for local test runs so third-party pytest plugins from dependencies do not interfere with Jesse's pinned `pytest` version.
- Use `./scripts/run-jesse-strategy-suite.sh` when the change touches framework-level strategy behavior or the evaluation harness.

### Jesse-Rust Integration
- When using Rust functions, **assume they exist** - don't add existence checks
- Update Python code to call new Rust implementations
- Build jesse-rust locally and run tests to verify integration
- Performance-critical code should be delegated to jesse-rust when possible

## File Structure
- `jesse/` - Main source code
  - `indicators/` - Technical indicators
  - `modes/` - Backtest, optimize, import modes, monte carlo, etc
  - `routes/` - FastAPI route handlers
  - `services/` - data services, etc
  - `strategies/` - Base strategy classes
  - `store/` - State management
- `tests/` - Test suite
- `storage/` - Logs and temporary files
- `requirements.txt` - Python dependencies
- `setup.py` - Package configuration

## Testing Strategy

### Unit Tests
- Run `pytest` after every change if asked in the conversation.
- Maintain or improve test coverage
- Add tests for new features if asked in the conversation.
- Fix failing tests immediately

## Related Repositories
This repository is the foundation of the Jesse ecosystem:
- **jesse-live** - Depends heavily on jesse for live trading
- **jesse-rust** - Performance layer integrated into jesse
- **dashboard-v1** - Frontend that consumes jesse's API
- **bot** - Jesse project instance that runs the framework
- **laravel-jesse-trade** - Laravel project that contains the api1 backend of the jesse-trade website.
- **go-jesse-trade/backend** - Go project that contains the api2 backend of the jesse-trade website.
- **go-jesse-trade/frontend** - NuxtJS project that contains the frontend of the jesse-trade website.
- **strategy-executor** - Go project that contains the strategy executor microservice used to execute strategies submitted by the users of the website.
