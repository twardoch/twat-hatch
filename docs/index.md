# twat-hatch

**twat-hatch** is a [twat](https://github.com/twardoch/twat) plugin that scaffolds
Python packages and plugins with a consistent, opinionated layout:

- `src/` layout with `hatchling` + `hatch-vcs` build backend
- Jinja2-powered theme templates for `package`, `plugin`, and `plugin-host` roles
- Interactive or non-interactive CLI via `twat-hatch init`
- GitHub Actions CI, pre-commit config, MkDocs docs (optional)

## Role in the twat ecosystem

`twat-hatch` is registered as a twat plugin entry-point (`twat.plugins → hatch`).
Running `twat hatch …` or using the standalone `twat-hatch` command bootstraps new
packages that are themselves ready to publish on PyPI.

## Installation

```bash
pip install twat-hatch
```

Or, as part of the full twat suite:

```bash
pip install "twat[all]"
```

## Quick example

```bash
# Interactive wizard — writes twat-hatch.toml
twat-hatch init

# Generate files from the config
twat-hatch create

# Non-interactive (CI / scripted)
twat-hatch init \
  --name my-package \
  --author-name "Jane Smith" \
  --author-email jane@example.com \
  --github-username janesmith \
  --min-python 3,11 \
  --license MIT \
  --development-status "4 - Beta"
twat-hatch create
```

## Commands

| Command | Description |
|---|---|
| `twat-hatch init` | Write `twat-hatch.toml` (interactive or from flags) |
| `twat-hatch plugin-init` | Like `init` but defaults to plugin package type |
| `twat-hatch create` | Render templates from `twat-hatch.toml` |
| `twat-hatch config show` | Print an example config for a given package type |
| `twat-hatch version` | Print the installed version |
