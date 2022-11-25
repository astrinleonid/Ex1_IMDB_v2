from bs4 import BeautifulSoup
import requests



def html_open(url_name, header):
    """
    Opens web page at url_name
    Returns the soup of the whole page
    """
    # header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
    page = requests.get(url_name, headers = header)
    return BeautifulSoup(page.content, "html.parser")
