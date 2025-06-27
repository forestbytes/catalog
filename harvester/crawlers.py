import requests
from bs4 import BeautifulSoup
import re
import arrow
from dotenv import load_dotenv
import os
import uuid

load_dotenv()


def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    stripped_text = stripped_text.replace("\n", " ")
    return stripped_text


class FSGeodataHarvester:
    def __init__(self):
        self.base_url = "https://data.fs.usda.gov/geodata/edw/datasets.php"
        self.temp_folder = "./tmp"

    def download_metadata_files(self):
        metadata_urls = []

        resp = requests.get(self.base_url)
        soup = BeautifulSoup(resp.content, "html.parser")

        anchors = soup.find_all("a")
        for anchor in anchors:
            if anchor and anchor.get_text() == "metadata":
                metadata_urls.append(anchor["href"])

        # Download the metadata files
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        for u in metadata_urls:
            url = f"https://data.fs.usda.gov/geodata/edw/{u}"
            outfile_name = f"{self.temp_folder}/{u.split('/')[-1]}"

            if not os.path.exists(outfile_name):
                resp = requests.get(url)
                with open(outfile_name, "wb") as f:
                    f.write(resp.content)

    def parse_metadata(self):
        xml_files = [f for f in os.listdir(self.temp_folder) if f.endswith(".xml")]

        assets = []

        for xml_file in xml_files:
            url = f"https://data.fs.usda.gov/geodata/edw/edw_resources/meta/{xml_file}"
            with open(f"{self.temp_folder}/{xml_file}", "r") as f:
                soup = BeautifulSoup(f, "xml")
                if soup.find("title"):
                    title = strip_html_tags(soup.find("title").get_text())
                else:
                    title = ""

                desc_block = ""
                abstract = ""
                if soup.find("descript"):
                    desc_block = soup.find("descript")
                    abstract = strip_html_tags(desc_block.find("abstract").get_text())
                themekeys = soup.find_all("themekey")
                keywords = [tk.get_text() for tk in themekeys]
                idinfo_citation_citeinfo_pubdate = soup.find("pubdate")
                if idinfo_citation_citeinfo_pubdate:
                    modified = arrow.get(idinfo_citation_citeinfo_pubdate.get_text())
                else:
                    modified = ""

                # Generate a UUID4 (random UUID)
                unique_id = uuid.uuid4()
                asset = {
                    "id": unique_id,
                    "title": title,
                    "description": abstract,
                    "modified": modified,
                    "metadata_source_url": url,
                    "keywords": keywords,
                }

                assets.append(asset)

        return assets


class DataHubHarvester:
    def __init__(self):
        self.source_url = "https://data-usfs.hub.arcgis.com/api/feed/dcat-us/1.1.json"
        self.temp_folder = "./tmp"


class RDAHarvester:
    def __init__(self):
        self.source_url = "https://www.fs.usda.gov/rds/archive/webservice/datagov"
        self.temp_folder = "./tmp"



def main():
    fsgeodata = FSGeodataHarvester()
    fsgeodata.download_metadata_files()
    fsgeodata_documents = fsgeodata.parse_metadata()


if __name__ == "__main__":
    main()
