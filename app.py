from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os
import json

load_dotenv()

SOURCE_URL = "https://data-usfs.hub.arcgis.com/api/feed/dcat-us/1.1.json"
LOCAL_FILE_NAME = "usfs-hub-dcat-us.json"

def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    stripped_text = stripped_text.replace("\n", " ")
    return stripped_text


def download_source_file(url):
    """Download the source file from the given URL and save it locally."""
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")

    resp = requests.get(url)
    with open(f"./tmp/{LOCAL_FILE_NAME}", "w") as f:
        f.write(resp.content.decode("utf-8"))

def read_json_file(file_path):
    """Parse the JSON file and return its content."""
    with open(file_path, "r") as f:
        return json.load(f)
    
def extract_data(json_data: dict) -> list:
    """Extract specific data from the JSON content."""
    
    extracted_data = []
    
    for item in json_data.get("dataset", []):
        data = {
            "title": item.get("title"),
            "identifier": item.get("identifier"),
            "description": strip_html_tags(item.get("description")),
            "url": item.get("url"),
            
        }
        extracted_data.append(data)

    return extracted_data


if __name__ == "__main__":
    # download_source_file(SOURCE_URL)
    # print(f"Downloaded {SOURCE_URL} to ./tmp/{LOCAL_FILE_NAME}")
    json_data = read_json_file(f"./tmp/{LOCAL_FILE_NAME}")
    data = extract_data(json_data)
    print(f"Extacted {len(data)} items.")

    cnt = 0
    for item in data:
        if "item.html?id=" in item["identifier"]:
            cnt += 1
    print(cnt)
    
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# async def main():
#     llm_strategy = LLMExtractionStrategy(
#         provider="gemini/gemini-2.0-flash",  # LLM provider (Gemini, OpenAI, etc.)
#         api_token=os.getenv("GEMINI_API_KEY"),  # API key for authentication
#         schema=BusinessData.model_json_schema(),  # JSON schema of expected data
#         extraction_type="schema",  # Use structured schema extraction
#         instruction=(
#             "Extract all business information: 'name', 'address', 'website', "
#             "'phone number' and a one-sentence 'description' from the content."
#         ),
#         input_format="markdown",  # Define input format
#         verbose=True,  # Enable logging for debugging
#     )

#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url="https://data-usfs.hub.arcgis.com/api/feed/dcat-us/1.1.json",
#         )
#         resp = result.json
#         print(resp)
        
# if __name__ == "__main__":
#     asyncio.run(main())