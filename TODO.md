# TODO: Streamlining `twat-hatch` Codebase (MVP v1.0)

- [x] Analyze `cleanup.py` and `repomix` usage.
- [x] Review `PyVer` in `src/twat_hatch/utils.py` and simplify its parsing logic.
- [x] Examine `PackageConfig.from_toml` in `src/twat_hatch/hatch.py` for simplification opportunities.
- [x] Simplify `.gitignore` file.
- [x] Review CLI arguments in `src/twat_hatch/__main__.py`.
- [x] Review comments in `pyproject.toml.j2` templates and simplify.
- [x] Create `PLAN.md` with the detailed plan. (Consolidated existing implicit plan and outcomes).
- [x] Create `TODO.md` (this file).
- [x] Update `CHANGELOG.md` to record all modifications made during this streamlining effort. (Note: `LOG.md` is the primary changelog, `CHANGELOG.md` was created for this exercise).
- [x] Verify `VERSION.txt` and `LOG.md` are up-to-date.
- [ ] Perform a final review of all changes.
- [ ] Run `cleanup.py update` (includes checks like `ruff`, `mypy`, `pytest`) to ensure the codebase is clean and tests pass.
- [ ] Submit the changes with a comprehensive commit message.
