from bs4 import BeautifulSoup

def strip_html(text):
    soup = BeautifulSoup(text, features="lxml")
    return soup.get_text()



# def hello() -> str:
#     return "Hello from catalog!"
