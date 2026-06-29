# Configuration Reference

`twat-hatch init` writes a `twat-hatch.toml` file. You can also write it by hand.

## Example — standalone package

```toml
[project]
packages = ["my-package"]
output_dir = "."

[author]
name = "Your Name"
email = "you@example.com"
github_username = "yourusername"

[package]
min_python = "3.11"
license = "MIT"
development_status = "4 - Beta"

[features]
mkdocs = false
vcs = true
github_actions = true
```

## Example — plugin

```toml
[project]
packages = ["my-host-awesome"]
plugin_host = "my-host"
output_dir = "."

[author]
name = "Your Name"
email = "you@example.com"
github_username = "yourusername"

[package]
min_python = "3.11"
license = "MIT"
development_status = "3 - Alpha"

[features]
vcs = true
```

## Field reference

### `[project]`

| Key | Type | Description |
|---|---|---|
| `packages` | list of str | Distribution names of packages to scaffold |
| `plugin_host` | str (optional) | Host package name; triggers plugin theme for non-host packages |
| `output_dir` | str | Where to write generated packages (default: `.`) |

### `[author]`

| Key | Type | Description |
|---|---|---|
| `name` | str | Author full name |
| `email` | str | Author email |
| `github_username` | str | GitHub username (used in URLs and workflows) |

### `[package]`

| Key | Type | Description |
|---|---|---|
| `min_python` | str | Minimum Python version e.g. `"3.11"` |
| `max_python` | str (optional) | Maximum Python version |
| `license` | str | License identifier e.g. `"MIT"` |
| `development_status` | str | PyPI trove classifier suffix e.g. `"4 - Beta"` |

### `[features]`

| Key | Default | Description |
|---|---|---|
| `vcs` | `true` | Run `git init` and make an initial commit |
| `mkdocs` | `false` | Apply MkDocs Material theme template |
| `github_actions` | `true` | Include `.github/workflows/` in scaffold |
