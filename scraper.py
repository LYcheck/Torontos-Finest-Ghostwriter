import requests
import os
from bs4 import BeautifulSoup
import re

API_KEY = GKEY

def getArtistInfo(name, pg):
    url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + API_KEY}
    toSearch = url + '/search?per_page=10&page=' + str(pg)
    data = {'q': name}
    resp = requests.get(toSearch, data=data, headers=headers)
    return resp

def getSongUrls(name, songQty):
    pg = 1
    songs = []

    while True:
        response = getArtistInfo(name, pg)
        json = response.json()
        songInfo = []

        for result in json['response']['hits']:
            if name.lower() in result['result']['primary_artist']['name'].lower():
                songInfo.append(result)

        for song in songInfo:
            if (len(songs) < songQty):
                songs.append(song['result']['url'])

        if (len(songs) == songQty):
            break
        else:
            pg += 1

    print('Found {} songs by {}'.format(len(songs), name))
    return songs

def scrapeLyrics(url):
    pg = requests.get(url)
    html = BeautifulSoup(pg.text, 'html.parser')
    if html.find('div', class_='lyrics') is not None:
        lyrics = html.find('div', class_='lyrics').get_text()
    else:
        lyrics = ''
    #TODO parse out identifiers
    #TODO reduce whitespace
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
    return lyrics

def lyricsToFile(name, songQty):
    fl = open('lyrics/' + name.lower() + '.txt', 'wb')
    urls = getSongUrls(name, songQty)

    for url in urls:
        lyrics = scrapeLyrics(url)
        fl.write(lyrics.encode("utf8"))

    fl.close()

    numLines = sum(1 for line in open('lyrics/' + name.lower() + '.txt', 'rb'))
    print('Wrote {} lines to file from {} songs'.format(numLines, songQty))

lyricsToFile('Drake', 200)