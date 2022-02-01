from lxml import etree


def is_equivalent(xml_1: str, xml_2: str):
    root_1 = etree.fromstring(bytes(xml_1, "utf-8"))
    root_2 = etree.fromstring(bytes(xml_2, "utf-8"))
    tree_1 = etree.ElementTree(root_1)
    tree_2 = etree.ElementTree(root_2)

    set_1 = set(etree.tostring(i, method="c14n") for i in tree_1.getroot())
    set_2 = set(etree.tostring(i, method="c14n") for i in tree_2.getroot())

    if set_1 != set_2:
        print(xml_1)
        print(xml_2)
        print(set_1)
        print(set_2)

    return set_1 == set_2
