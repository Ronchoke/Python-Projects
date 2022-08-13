"""This code finds the top 100 most popular songs by parsing and without using OOP
the HOT 100 index by Billboard (https://www.billboard.com/charts/hot-100/)
plots the 100 most used words in all these songs lyrics
and shows the top 10 artists that use the most words"""

import string
import matplotlib.pyplot as plt
# import re
import requests

from bs4 import BeautifulSoup as Soup
from typing import Union


def get_content_from_url(url: str) -> Soup:
    """ This function requests the content of a given HTML url,
     parses it and returns a list of all relevant content under the text_specifier.
    :param url: str
    :return: list
    """
    # Connect to url and check response
    req = requests.get(url)
    if req.status_code != 200:
        print(url)
        raise ConnectionError

    # Get content from artist page
    return Soup(req.text, 'html.parser')


def find_song_title_link(song_title: str, songs: list) -> str:
    """This function iterates through HTML syntax from https://www.lyrics.com/ website
    parsed by the get_content_from_url function
    and find's the relative link to the song_title lyrics.
    :param song_title: str
    :param songs: list of HTML syntax content
    :return: str, relative path to url
    """
    for song in songs:
        find_song_title = song.a.text.lower()
        if '(' in find_song_title:
            find_song_title = find_song_title.split(' (')[0]
        if song_title.lower() == find_song_title:
            return song.find('a').attrs['href']
    return ''


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
    if "With" in artist:
        artist = artist.split(' With')[0]
    if 'Featuring' in artist:
        artist = artist.split(' Featuring')[0]
    if '&' in artist:
        artist = artist.split(' & ')[0]

    # Handle bracketed song title synonyms
    if '(' in song_title:
        song_title = song_title.split(' (')[0]

    # Create Artist page URL address
    base = 'https://www.lyrics.com/'
    url = base + 'artist/' + artist.lower().replace(' ', '+')
    relative_path = ''

    content = get_content_from_url(url)
    songs = content.find_all('td', {'class': 'tal qx'})

    # Non-specific artist name return empty string, page is redirected to a search artist page
    if len(songs) == 0:
        # Look-Up in all Relevant artist
        # content = get_content_from_url(url)
        artists = content.find_all('td', {'class': 'tal fx'})

        # Search in all matching artists for the song
        for artist_link in artists:
            # Link to artist page
            # if artist_link.a is None:
                # continue
            try:
                url = base + artist_link.a.attrs['href']
            except AttributeError:
                continue
            content = get_content_from_url(url)
            songs = content.find_all('td', {'class': 'tal qx'})
            relative_path = find_song_title_link(song_title, songs)
            if relative_path:
                break
    else:
        relative_path = find_song_title_link(song_title, songs)

    return base + relative_path


def get_lyrics(song_title: str, artist: str) -> Union[str, None]:
    """The get_lyrics function gets the lyrics for a song_title,
    from https://www.lyrics.com website
    and return all the lyrics

    :param song_title: str.
    :param artist: str
    :return: lyrics: str. None if no URL was found.
    """
    url = get_full_url_to_lyrics(song_title, artist)
    if url is None:
        return ''

    lyr_page = get_content_from_url(url)
    lyrics = lyr_page.find('pre', {'id': 'lyric-body-text'})  # , limit=1)
    return lyrics.text


def count_words_in_text(text: str) -> dict:
    """Counts the number of unique words in a given string.
    :param text: str
    :return: word_count: dict
    """
    # Check input validation
    if text is '':
        return dict()
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

    content = get_content_from_url(url)
    chart_list = content.find_all('ul', class_="o-chart-results-list-row")

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


def merge_all_word_counts(song_word_count: dict, tot_word_count: dict) -> dict:
    """Sums the word counts of all the various song_count dictionaries
    :param song_word_count: dict
    :param tot_word_count: dict
    :return: tot_word_count: dict
    """
    for word in song_word_count.keys():
        try:
            tot_word_count[word] = tot_word_count[word] + song_word_count[word]
        except KeyError:
            tot_word_count[word] = song_word_count[word]
    return tot_word_count


def merge_dictionaries_by_key(songs_dict, key):
    """This function runs through a dictionary with values of type dictionary,
    and merges the values's values by the key given (value[key]).
    :param songs_dict: dict, to each key, the value is of type(dict)
    :param key: str, the key within the songs_dict value dictionary to be used (value[key])
    :return: tot_word_count: dict
    """
    tot_word_count = dict()
    for ranked_song_info in songs_dict.values():
        tot_word_count = merge_all_word_counts(ranked_song_info[key], tot_word_count)
    return tot_word_count


def plot_most_used_words(tot_word_count):
    big2small = sorted(tot_word_count.items(), key=lambda d: d[1], reverse=True)
    big2small = big2small[:101]
    words = [i[0] for i in big2small]
    count = [i[1] for i in big2small]

    plt.figure(figsize=(20, 5))
    plt.bar(words, count, align="edge")
    plt.tick_params(axis='x', rotation=90, pad=10, labelsize='large')
    plt.xlabel('Words')
    plt.ylabel('Counts')
    plt.show()


def main():
    songs_dict = get_top_100_songs()
    tot_word_count = merge_dictionaries_by_key(songs_dict, 'Word count')
    plot_most_used_words(tot_word_count)


if __name__ == "__main__":
    main()
