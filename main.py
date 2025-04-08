from rdflib import Graph, Literal, RDF, URIRef, BNode
# rdflib knows about quite a few popular namespaces, like W3C ontologies, schema.org etc.
from rdflib.namespace import FOAF , XSD, DCAT
from catalog.crawlers import (
    FSGeodata
)

fsgeodata = FSGeodata()

def main():
    # fsgeodata.get_metadata_urls()
    # fsgeodata.download_metadata()
    fsgeodata.parse_metadata()

    fsgeodata_assets = fsgeodata.assets

    # Create a Graph
    g = Graph()
    g.bind("dcat", DCAT)
    bnode = BNode()  # Create a blank node for the FSGeodata resource

    # Add triples using store's add method.
    g.add((bnode, DCAT.Catalog, DCAT.CatalogRecord))
    #g.add((bnode, FOAF.nick, Literal("", lang="foo")))
    #g.add((donna, FOAF.name, Literal("Donna Fales")))
    # fsgeodata_rdf = URIRef(f"{fsgeodata.base_url}")

    # # term.bind(XSD.string, complex)
    # g.add((fsgeodata_rdf, DCAT, DCAT.Document))
    # for asset in fsgeodata_assets:
    #     pass
    #     # Create an RDF URI node to use as the subject for multiple triples
    #     # g.add((fsgeodata_rdf, FOAF.title, Literal(f"{asset['title']}", datatype=XSD.string)))
    #     # g.add((fsgeodata_rdf, FOAF.description, Literal(f"{asset['description']}", datatype=XSD.string)))

    # # for s, p, o in g:
    #     print((s, p, o))
    # for stmt in g:
    #    print(stmt)
    v = g.serialize(format="xml")
    print(v)

if __name__ == "__main__":
    main()


""""
This example shows how :meth:`rdflib.term.bind` lets you register new
mappings between literal datatypes and Python objects


from rdflib import XSD, Graph, Literal, Namespace, term

if __name__ == "__main__":
    # Complex numbers are not registered by default
    # No custom constructor/serializer needed since
    # complex('(2+3j)') works fine
    term.bind(XSD.complexNumber, complex)

    # Create a complex number RDFlib Literal
    EG = Namespace("http://example.com/")
    c = complex(2, 3)
    l = Literal(c)  # noqa: E741

    # Add it to a graph
    g = Graph()
    g.add((EG.mysubject, EG.myprop, l))
    # Print the triple to see what it looks like
    print(list(g)[0])
    # prints: (
    #           rdflib.term.URIRef('http://example.com/mysubject'),
    #           rdflib.term.URIRef('http://example.com/myprop'),
    #           rdflib.term.Literal(
    #               '(2+3j)',
    #               datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#complexNumber')
    #           )
    #         )

    # Round-trip through n3 serialize/parse
    g2 = Graph().parse(data=g.serialize())

    l2 = list(g2)[0]
    print(l2)

    # Compare with the original python complex object (should be True)
    # l2[2] is the object of the triple
    assert isinstance(l2[2], Literal)
    print(l2[2].value == c)
"""
