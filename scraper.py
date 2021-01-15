import requests
import os
from bs4 import BeautifulSoup
import re

API_KEY = gkey

# formats and sends a request to gather information on an artist
def getArtistInfo(name, pg):
    url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + API_KEY}
    toSearch = url + '/search?per_page=10&page=' + str(pg) # req structure as per genius standard
    data = {'q': name}
    resp = requests.get(toSearch, data=data, headers=headers)
    return resp # returns API response with necessary data

def getSongUrls(name, songQty):
    pg = 1
    songs = []

    # loops through each page in artist discography
    while True:
        response = getArtistInfo(name, pg)
        json = response.json() # parses response to json, stores in var
        songInfo = []

        for result in json['response']['hits']: # loops through all songs returned by artist
            if name.lower() in result['result']['primary_artist']['name'].lower(): # if artist is primary on the song, append
                songInfo.append(result)

        for song in songInfo: # loops through array of primary artist songs, appends to match specified song quantity
            if (len(songs) < songQty):
                songs.append(song['result']['url']) # appends url if condition met

        if (len(songs) == songQty): # when quantity of songs is met, return
            break
        else:
            pg += 1 # otherwise, continue searching by incrementing search page

    print('Preparing to scrape {} songs by artist {}'.format(len(songs), name))
    return songs

def scrapeLyrics(url):
    pg = requests.get(url) # returns status code of specified url, parses afterwards using BS4
    html = BeautifulSoup(pg.text, 'html.parser')
    if html.find('div', class_='lyrics') is not None: # making sure div exists with lyrics class, gets text
        lyrics = html.find('div', class_='lyrics').get_text()
    else:
        lyrics = ''
    #TODO parse out identifiers
    #TODO reduce whitespace
    #lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
    return lyrics

def lyricsToFile(name, songQty):
    fl = open('lyrics/' + name.lower() + '.txt', 'wb') # opens txt
    urls = getSongUrls(name, songQty)

    for url in urls:
        lyrics = scrapeLyrics(url) # scrapes all lyrics in url list, appends to file
        fl.write(lyrics.encode("utf8"))

    fl.close()

    numLines = sum(1 for line in open('lyrics/' + name.lower() + '.txt', 'rb'))
    print('{} lines, {} songs'.format(numLines, songQty))

lyricsToFile('Drake', 200)