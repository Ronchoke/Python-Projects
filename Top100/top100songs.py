"""This code finds the top 100 most popular songs by parsing and without using OOP
the HOT 100 index by Billboard (https://www.billboard.com/charts/hot-100/)
plots the 100 most used words in all these songs lyrics
and shows the top 10 artists that use the most words"""

# import string
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
    if type(song_title) is not str or type(artist) is not str:
        raise TypeError("Input type must be string.")
    if song_title == '':
        raise ValueError("No Song Title inserted")
    if artist == '':
        raise ValueError("Artist\'s Name must be given")

    if '&' in artist:
        artist = artist.split(' & ')[0]

    url = 'https://www.lyrics.com/artist/' + artist.split(' ')[0].lower()

    for i in range(1, len(artist.split())):
        url = url + '%20' + artist.split(' ')[i].lower()

    r = requests.get(url)
    if r.status_code != 200:
        raise ConnectionError

    container = Soup(r.text, 'html.parser')
    songs = container.find_all('td', {'class': 'tal qx'})

    if len(songs) == 0:
        raise ValueError("Artist not found, check input for typos")

    base = 'https://www.lyrics.com'
    to_lyr = ''
    for i in range(len(songs)):
        if songs[i].a is None:
            pass
        elif songs[i].a.text.lower() == song_title.lower():
            to_lyr = songs[i].a.attrs['href']
        else:
            pass

    if to_lyr == '':
        raise ValueError("Title not found, check song input for typos")

    return base + to_lyr


def __main__():
    song_title = 'None'
    artist = "the Beatles"
    print(get_full_url_to_lyrics(song_title, artist))


if __name__ == "__main__":
    __main__()
