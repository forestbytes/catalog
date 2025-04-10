import os, glob
from catalog.crawlers import (FSGeodata)
from neo4j import GraphDatabase
from bs4 import BeautifulSoup
from catalog import strip_html

URI = "bolt://localhost:7687"
AUTH = tuple(os.environ.get("NEO4J_AUTH").split("/"))

fsgeodata = FSGeodata()


def deltete_neo4J_data():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.run("MATCH (n:Asset) DETACH DELETE n")


def load_neo4J_data():
    print("Loading data into Neo4J...")

    deltete_neo4J_data()

    with GraphDatabase.driver(URI, auth=AUTH) as driver:

        # def create_constraints(tx):
        #     tx.run("CREATE CONSTRAINT assets IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE")

        directory = "./data/fsgeodata"
        file_list = glob.glob(f"{directory}/*.xml")

        assets = []
        idx = 1
        for file in file_list:
            with open(file, "r", encoding="utf-8") as f:
                print(file)
                soup = BeautifulSoup(f.read(), features="xml")
                try:
                    title = strip_html(f"{soup.find("title").get_text().strip().replace("'", "").replace('"', '')}")
                    desc_block = soup.find("descript")
                    abstract = strip_html(desc_block.find("abstract").get_text().strip().replace("'", "").replace('"', ''))
                    themekeys = soup.find_all("themekey")
                    keywords = [tk.get_text().strip() for tk in themekeys]

                    assets.append(
                        {
                            "id": idx,
                            "title": title,
                            "description": abstract
                        },
                    )
                except Exception as e:
                    print(e)
                    continue

            idx += 1

        with driver.session() as session:
            for asset in assets:
                query = f'CREATE (a:Asset {{id: "{asset['id']}", title: "{asset["title"]}", description: "{asset["description"]}"}})'
                session.run(query)


        #with driver.session() as session:

            # session.write_transaction(create_constraints)

            # assets = [
            #     {
            #         "id": "asset1",
            #         "title": "Asset 1",
            #         "description": "This is the first asset."
            #     },
            #     {
            #         "id": "asset2",
            #         "title": "Asset 2",
            #         "description": "This is the second asset."
            #     },
            #     {
            #         "id": "asset23",
            #         "title": "Asset 3",
            #         "description": "This is the third asset."
            #     }
            # ]

            # for asset in assets:
            #     query = f"CREATE (a:Asset {{id: '{asset['id']}', title: '{asset['title']}'}})"
            #     session.run(query)



        # driver.verify_connectivity()
        # with driver.session() as session:
        #     session.run("CREATE (a:Person {name: 'Alice', title: 'Engineer'})")
        #     session.run("CREATE (a:Person {name: 'Bob', title: 'Manager'})")
        #     session.run("MATCH (a:Person),(b:Person) "
        #                 "WHERE a.name = 'Alice' AND b.name = 'Bob' "
        #                 "CREATE (a)-[r:KNOWS]->(b) "
        #                 "RETURN type(r)")

        # conn.query('CREATE CONSTRAINT papers IF NOT EXISTS ON (p:Paper)     ASSERT p.id IS UNIQUE')
        # conn.query('CREATE CONSTRAINT authors IF NOT EXISTS ON (a:Author) ASSERT a.name IS UNIQUE')
        # conn.query('CREATE CONSTRAINT categories IF NOT EXISTS ON (c:Category) ASSERT c.category IS UNIQUE')

def main():
    # fsgeodata.get_metadata_urls()
    # fsgeodata.download_metadata()
    # fsgeodata.parse_metadata()
    # fsgeodata_assets = fsgeodata.assets
    # for asset in fsgeodata_assets:
    #     print(asset)

    load_neo4J_data()

if __name__ == "__main__":
    main()
