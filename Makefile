.PHONY: gh-deploy build-chromadb

gh-deploy:
	uv run mkdocs gh-deploy

build-chromadb:
	uv run catalog build-fs-chromadb
