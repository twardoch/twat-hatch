# Contributing to {name}

First off, thanks for taking the time to contribute! ❤️

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/{github_username}/{name}.git
   cd {name}
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```

2. Make your changes and ensure tests pass:
   ```bash
   hatch run test
   ```

3. Format and lint your code:
   ```bash
   hatch run lint
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add some feature"
   ```

5. Push to your fork:
   ```bash
   git push origin feature-name
   ```

6. Open a Pull Request!

## Code Style

We use:
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [Black](https://github.com/psf/black) for code formatting
- [MyPy](https://github.com/python/mypy) for type checking

## Running Tests

```bash
# Run all tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run type checking
hatch run type-check

# Run linting
hatch run lint
```

## Documentation

We use MkDocs with the Material theme. To preview documentation locally:

```bash
hatch run docs-serve
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a new GitHub release
4. The CI/CD pipeline will automatically publish to PyPI

## Questions?

Feel free to open an issue or reach out to {author_name} ({author_email}). 