import sys
from datetime import datetime
import json
import logging
import grequests
from bs4 import BeautifulSoup
from request_open import html_open
from grequests_open import open_movies_w_grequests


# logging.basicConfig(format='%(asctime)s-%(levelname)s+++FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
#                     level=logging.DEBUG)

# Create logger
logger = logging.getLogger('IMDB_parse')
logger.setLevel(logging.DEBUG)

# Create Formatter
formatter = logging.Formatter(
    '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')
#
# file_handler = logging.FileHandler('movies.log')
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)


def open_movies_w_requests(movies):

    """
    Parses links from the list using requests package

    """

    for i in range(config["batch_size"]):
        for num, href in movies[i]:
            try:
                page = html_open(href, config["header"])
            except Exception as er:
                logger.error("Failed to establish connection to the link %s", href)
                raise Exception(er)

            (title, director) = parse_details(page)
            print(f"{num}  Title : {title}, Director: {director}")


def parse_movie_pages(soup, mode ='r'):

    """
    Extracts links to the movie pages from the starter page and parse the pages under the links

    """

    main_section = soup.find(class_ =  config["tags"]["main_section_class"])
    if len(main_section) == 0:
        logger.error(f'Main section : item not found')
    movies_list = main_section.find('tbody', class_= config["tags"]["mov_list_class"])
    if len(movies_list) == 0:
        logger.error(f'List of te movies section: item not found')
    movies_items = movies_list.find_all('tr')
    if len(movies_items) == 0:
        logger.error(f'List of the movies: items not found')
    movies = []

    for i, movie in enumerate(movies_items):
        movie_href = movie.find("a", href=True)["href"]
        if movie_href == []:
            logger.error(f'Movie link: item not found')
        batch_no = i // config["batch_size"]
        if len(movies) == batch_no:
            movies.append([])

        movies[batch_no].append((i, config["target_url"] + movie_href))

    logger.info(f'%s links sucsessfully parsed, divided into %s batches',
                 len(movies) * config["batch_size"], len(movies))
    print("List of the links successfuly formed, starting to parse individual movie pages")
    time_start = datetime.now()
    if mode == 'r':
        open_movies_w_requests(movies)
    elif mode == 'g':
        for batch_num, batch in enumerate(movies):
            try:
                pages = open_movies_w_grequests(batch, config["header"])
            except Exception as er:
                logger.error("Failed to establish connection to "
                             "one or more individual movie pages in a batch %s", batch_num)
                raise Exception(er)
            logger.info("Links in the batch %s sucsessfully opened, parsing info", batch_num)
            print(f"Links in the batch {batch_num} sucsessfully opened, parsing info")
            for index, page in pages:
                soup = BeautifulSoup(page.content, "html.parser")
                (title, director) = parse_details(soup)
                print(f"{index}  Title : {title}, Director: {director}")
    time_end = datetime.now()
    print("Time elapsed : ", time_end - time_start)
    logger.info("\n%s Pages parsed successfully\n Time elapsed : %s",
                len(movies)*config["batch_size"], str(time_end - time_start))


def parse_details(soup):
    """
    Parse individual movie page
    """

    title = soup.find('h1').text.strip()
    if len(title) == 0:
        logger.error(f'Movie title: item not found')
    director_container = soup.find('div', class_= config["tags"]["director_button_class"])
    if len(director_container) == 0:
        logger.error(f'Movie director: item not found')
    directors = director_container.find_all('li')
    logger.info(f"Page of the movie %s sucsessfully parsed", title)
    return (title, "   ".join([director.text.strip() for director in directors]))

def main(mode):

    logger.info("\n\nParsing IMDB website \n  %s  \nUsing module %s\n\n",
                str(datetime.now()), (lambda m: "requests" if m == "r" else "grequests")(mode))
    try:
        page = html_open(config["target_url"] + config["start_page"], config["header"])
    except Exception as er :
        logger.error("Failed to establish connection to the page %s",config["target_url"] + config["start_page"])
        raise Exception(er)

    parse_movie_pages(page, mode)

if __name__ == "__main__":

    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # with open(config["log_file"], 'w') as log_file:
    #     log_file.write("parsing IMDB website \n" + str(datetime.now()) + "\n\n")


    file_handler = logging.FileHandler(config["log_file"])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    mode = 'r'
    if len(sys.argv) == 2:
        if sys.argv[1] == '-g':
            mode = 'g'
            print("Parsing using grequests")
        elif sys.argv[1] == '-r':
            mode = 'r'
            print("Parsing using requests")
        else:
            raise ValueError("Wrong argument" + config["usage"])

    if len(sys.argv) > 2:
        raise TypeError("Wrong number of arguments" + config["usage"])

    main(mode)

    # logger.info("\n\nParsing IMDB website \n  %s  \nUsing module %s\n\n",
    #             str(datetime.now()), (lambda m: "requests" if m == "r" else "grequests")(mode))

    # a = (lambda m: "requests" if m == "r" else "grequests")(mode)
    # print(a)

    # parse_movie_pages(html_open(config["target_url"] + config["start_page"], config["header"]), mode)