import click
from crawlers import FSGeodataHarvester, DataHubHarvester, RDAHarvester, merge_docs, find_duplicate_documents


@click.group()
def cli():
    pass

def _harvest_fsgeodata():
    """Harvest data from FS Geodata."""
    fsgeodata = FSGeodataHarvester()
    fsgeodata.download_metadata_files()
    fsgeodata_documents = fsgeodata.parse_metadata()
    return fsgeodata_documents

@click.command()
def harvest_fsgeodata():
    """Harvest data from FS Geodata."""
    documents = _harvest_fsgeodata()
    click.echo(f"Extracted {len(documents)} items from FS Geodata.")


def _harvest_datahub():
    """Harvest data from DataHub."""
    datahub = DataHubHarvester()
    datahub.download_metadata_files()
    datahub_documents = datahub.parse_metadata()
    return datahub_documents


@click.command()
def harvest_datahub():
    """Harvest data from DataHub."""
    documents = _harvest_datahub()
    print(f"Extracted {len(documents)} items from DataHub.")


def _harvest_rda():
    """Harvest data from RDA."""
    rda = RDAHarvester()
    rda.download_metadata_files()
    rda_documents = rda.parse_metadata()
    return rda_documents


@click.command()
def harvest_rda():
    """Harvest data from RDA."""
    documents = _harvest_rda()
    print(f"Extracted {len(documents)} items from RDA.")


@click.command()
@click.pass_context
def harvest_all(ctx):
    """Harvest data from all sources."""
    fsgeodata_docs = _harvest_datahub()
    datahub_docs = _harvest_fsgeodata()
    rda_docs = _harvest_rda()

    documents = fsgeodata_docs + datahub_docs + rda_docs
    print(f"Total documents extracted: {len(documents)}")

    documents = merge_docs(fsgeodata_docs, datahub_docs, rda_docs)

    duplicates = find_duplicate_documents(documents)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate documents based on title:")
        for dup in duplicates:
            print(f"- {dup['id']}: {dup['title']}, {dup['keywords']}")

    print(f"{len(documents)} documents after merging and deduplication.")


cli.add_command(harvest_fsgeodata)
cli.add_command(harvest_datahub)
cli.add_command(harvest_rda)
cli.add_command(harvest_all)


if __name__ == '__main__':
    cli()

# def main():

#     print("Hello from harvester!")
#     fsgeodata = FSGeodataHarvester()


# if __name__ == "__main__":
#     main()


# import click

# @click.command()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
# def hello(count, name):
#     """Simple program that greets NAME for a total of COUNT times."""
#     for x in range(count):
#         click.echo(f"Hello {name}!")

# if __name__ == '__main__':
#     hello()
