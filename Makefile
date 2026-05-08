.DEFAULT_GOAL := test
.PHONY: lint test init publish docs

lint:
	uv run ruff check
test:
	uv run pytest
init:
	uv sync --locked
publish:
	uv build
	uv publish
	rm -fr build dist .egg records.egg-info
docs:
	cd _docs && $(MAKE) singlehtml
	cp -fR _docs/_build/singlehtml/* docs/
	cd ..
