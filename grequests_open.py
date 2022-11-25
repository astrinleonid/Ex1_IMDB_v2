from bs4 import BeautifulSoup
import grequests




def open_movies_w_grequests(movies, header):
    """
    Opens the batch of hrefs with grequests and returns the list of pages paired with their numbers
    """

    rs = (grequests.get(href, headers=header) for num, href in movies)
    pages = grequests.map(rs)
    return zip([i for i, h in movies], pages)

