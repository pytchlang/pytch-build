import markdown
from bs4 import BeautifulSoup


def soup_from_markdown_text(markdown_text):
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, "html.parser")
    return soup
