# Themes

Themes are Jinja2 template trees stored inside the package at
`src/twat_hatch/themes/`. They are composited in layers.

## Layer order

1. **`default/`** — always applied first; provides CI, pre-commit, license, README skeleton
2. **role theme** — one of `package/`, `plugin/`, or `plugin_host/`; adds role-specific source files
3. **`mkdocs/`** — optional; added when `features.mkdocs = true`

## Shared snippets

`_shared/` contains Jinja2 partials re-used across themes:

| Snippet | Purpose |
|---|---|
| `base.toml.j2` | Common pyproject.toml sections |
| `snippets/author.toml.j2` | `[project.authors]` block |
| `snippets/dependencies.toml.j2` | Runtime + optional deps |
| `snippets/development.toml.j2` | Dev-env hatch config |
| `snippets/features.toml.j2` | Ruff / mypy / coverage config |
| `snippets/package.toml.j2` | `[project]` metadata |
| `snippets/tools.toml.j2` | Hatch environment scripts |

## Template variables

Every template receives the following context:

| Variable | Type | Description |
|---|---|---|
| `name` | str | Distribution name (hyphens) |
| `import_name` | str | Import name (underscores) |
| `plugin_import_name` | str | Short plugin name (strips host prefix) |
| `author_name` | str | Author full name |
| `author_email` | str | Author email |
| `github_username` | str | GitHub username |
| `min_python` | str | Minimum Python version string |
| `max_python` | str \| None | Maximum Python version string |
| `license` | str | License identifier |
| `development_status` | str | PyPI classifier suffix |
| `use_mkdocs` | bool | Whether mkdocs theme was requested |
| `use_vcs` | bool | Whether to initialise git |
| `python_version_info` | dict | Pre-computed version metadata |

### `python_version_info` keys

| Key | Example | Description |
|---|---|---|
| `requires_python` | `">=3.11"` | pyproject.toml `requires-python` |
| `classifiers` | `["Programming Language :: Python :: 3.11", …]` | Trove classifiers |
| `ruff_target` | `"py311"` | Ruff `target-version` |
| `mypy_version` | `"3.11"` | mypy `python_version` |

## File naming conventions

- Files named `hidden.<name>` are written as `.<name>` (dot-files).
- Files named `__package_name__.<ext>` are written with `__package_name__`
  replaced by the package's `import_name`.
- All template files must end in `.j2`; the suffix is stripped on output.
