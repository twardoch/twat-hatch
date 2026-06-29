# Quick Start

## 1. Install

```bash
pip install twat-hatch
```

## 2. Scaffold a standalone package

```bash
mkdir my-project && cd my-project
twat-hatch init --name my-package \
  --author-name "Your Name" \
  --author-email you@example.com \
  --github-username yourusername \
  --min-python 3,11 \
  --license MIT
twat-hatch create
```

This writes a `my_package/` directory beside the config file.

## 3. Scaffold a plugin + its host

```bash
twat-hatch init \
  --name "my-host my-host-awesome" \
  --package-type plugin-host
# then for each plugin:
twat-hatch plugin-init \
  --name my-host-awesome \
  --plugin-host my-host
twat-hatch create
```

## 4. What gets generated

Every scaffold includes (via the `default` theme):

| File | Purpose |
|---|---|
| `pyproject.toml` | hatchling + hatch-vcs build config |
| `src/<pkg>/__init__.py` | Public API module |
| `src/<pkg>/__version__.py` | Auto-generated version (hatch-vcs) |
| `tests/test_package.py` | Minimal smoke test |
| `.github/workflows/push.yml` | CI: lint + test matrix |
| `.github/workflows/release.yml` | CD: publish to PyPI on tag |
| `.pre-commit-config.yaml` | ruff + mypy hooks |
| `README.md` | Starter readme |
| `LICENSE` | MIT (or chosen license) |
| `CLAUDE.md` / `AGENT.md` | AI assistant context files |
