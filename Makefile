.DEFAULT_GOAL := test
.PHONY: test init publish

test:
	uv run pytest
init:
	uv sync --locked
publish:
	uv build
	uv publish
	rm -fr build dist .egg records.egg-info
