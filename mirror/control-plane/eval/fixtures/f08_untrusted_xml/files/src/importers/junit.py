import xml.etree.ElementTree as ET


def parse_report(xml_text: str):
    root = ET.fromstring(xml_text)
    return [t.attrib["name"] for t in root.iter("testcase")]
