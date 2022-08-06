"""This code finds the top 100 most popular songs by parsing and without using OOP
the HOT 100 index by Billboard (https://www.billboard.com/charts/hot-100/)
plots the 100 most used words in all these songs lyrics
and shows the top 10 artists that use the most words"""

import string
# import matplotlib.pyplot as plt
import requests

from bs4 import BeautifulSoup as Soup


def get_full_url_to_lyrics(song_title: str, artist: str) -> str:
    """Gets the full link to the lyric's page for a song_title and artist name,
    from https://www.lyrics.com website and return all the lyrics.
    :param song_title: str.
    :param artist: str
    :return: url: str
    """
    # Check Input
    if type(song_title) is not str or type(artist) is not str:
        raise TypeError("Input type must be string.")
    if song_title == '':
        raise ValueError("No Song Title inserted")
    if artist == '':
        raise ValueError("Artist\'s Name must be given")

    # Handle multiple Artists
    if '&' in artist:
        artist = artist.split(' & ')[0]
    elif 'Featuring' in artist:
        artist = artist.split(' Featuring')[0]

    # Create Artist page URL address
    url = 'https://www.lyrics.com/artist/' + artist.split(' ')[0].lower()
    for i in range(1, len(artist.split())):
        url = url + '%20' + artist.split(' ')[i].lower()

    # Connect to url and check response
    r = requests.get(url)
    if r.status_code != 200:
        raise ConnectionError

    # Get artist's page content
    container = Soup(r.text, 'html.parser')
    songs = container.find_all('td', {'class': 'tal qx'})

    # Non-existing artists return empty string
    if len(songs) == 0:
        # TODO: featuring artist fails here, see "Wait For U ,  Future Featuring Drake" example
        print(song_title, ", ", artist)
        raise ValueError("Artist not found, check input for typos")

    # Create song's page URL
    base = 'https://www.lyrics.com'
    to_lyr = ''
    for i in range(len(songs)):
        if songs[i].a is None:
            continue
        elif songs[i].a.text.lower() == song_title.lower():
            to_lyr = songs[i].a.attrs['href']
        else:
            continue

    # Un-found song titles
    if to_lyr == '':
        raise ValueError("Title not found, check song input for typos")

    return base + to_lyr


def get_lyrics(song_title: str, artist: str) -> str:
    """The get_lyrics function gets the lyrics for a song_title,
    from https://www.lyrics.com website
    and return all the lyrics

    :param song_title: str.
    :param artist: str
    :return: lyrics: str
    """
    url = get_full_url_to_lyrics(song_title, artist)

    # Connect to url and check response
    req = requests.get(url)
    if req.status_code != 200:
        raise ConnectionError

    # Parse for lyrics
    lyr_page = Soup(req.text, 'html.parser')
    return lyr_page.find('pre', {'id': 'lyric-body-text'}).text


def count_words_in_text(text: str) -> dict:
    """Counts the number of unique words in a given string.
    :param text: str
    :return: word_count: dict
    """
    # Check input validation
    if type(text) is not str:
        raise ValueError("Input must be string")

    # Clean rows from Text
    text.replace("\n", ' ')

    # Insert word without punctuations
    word_count = {}
    for word in text.split():
        word = word.strip(string.punctuation).lower()
        try:
            word_count[word] = word_count[word] + 1
        except KeyError:
            word_count[word] = 1
    return word_count


def get_top_100_songs() -> dict:
    """This function gets the top 100 songs as published on the
    Billboard hot-100 page (https://www.billboard.com/charts/hot-100)

    :return: songs_dict: dict
    """
    url = 'https://www.billboard.com/charts/hot-100'

    # Connect to url and check response
    page = requests.get(url)
    if page.status_code != 200:
        raise ConnectionError

    # Parse content
    page_content = Soup(page.content, 'html.parser')
    chart_list = page_content.find_all('ul', class_="o-chart-results-list-row")

    # Find all ranks, and correlating titles and artists
    songs_dict = {}
    for element in chart_list:
        rank = element.find('span', class_='a-font-primary-bold-l').string.strip('\n\t')
        song_title = element.find('h3', class_='a-no-trucate').string.strip('\n\t')
        artist = element.find('span', class_='a-no-trucate').string.strip('\n\t')

        lyrics = get_lyrics(song_title, artist)
        if rank not in songs_dict:
            songs_dict[rank] = {'Title': song_title,
                                'Artist': artist.replace(' &', ','),
                                'Word count': count_words_in_text(lyrics)}
        else:
            raise LookupError(f"parsing error. rank {rank} was already accounted for")

    return songs_dict


def __main__():
    # print(get_lyrics("Wait For U", "Future Featuring Drake"))
    get_top_100_songs()


if __name__ == "__main__":
    __main__()
