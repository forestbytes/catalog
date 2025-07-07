import json

from harvester import (
    _harvest_datahub,
    _harvest_fsgeodata,
    _harvest_rda,
    merge_docs,
    find_duplicate_documents,
)


def retrieve_docs():
    """Retrieve documents from various sources."""
    docs = []

    fsgeodata_docs = _harvest_fsgeodata()
    datahub_docs = _harvest_datahub()
    rda_docs = _harvest_rda()

    docs = merge_docs(fsgeodata_docs, datahub_docs, rda_docs)

    duplicates = find_duplicate_documents(docs)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate documents based on title:")
        for dup in duplicates:
            print(f"- {dup['id']}: {dup['title']}, {dup['keywords']}")

    return docs


def load_usfs_docs_into_postgres(docs):
    pass


def main():
    docs = retrieve_docs()
    print(f"Total documents extracted: {len(docs)}")

    with open("usfs_docs.json", "w") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
