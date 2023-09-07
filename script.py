import requests
import re
import yt_dlp as youtube_dl
import os
import json

from bs4 import BeautifulSoup

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

numResults = 10

def get_ids(input, numResults):
    videos = []

    url = f"https://www.youtube.com/results?search_query={input}"
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    for script in soup.find_all('script'):
        if(script.text.startswith('var ytInitialData = ')):
            searchDataRaw = script.text
            searchDataRaw = searchDataRaw.replace("var ytInitialData = ","")
            searchDataRaw = searchDataRaw[:len(searchDataRaw)-1]
            break
    
    searchData = json.loads(searchDataRaw)

    c = 1
    while c < numResults+1:
        videoData = searchData.get('contents').get('twoColumnSearchResultsRenderer').get('primaryContents').get('sectionListRenderer').get('contents')[0].get('itemSectionRenderer').get('contents')[c]

        for key in videoData:
            if key == 'videoRenderer':
                title = videoData.get('videoRenderer').get('title').get('runs')[0].get('text')
                videoId = videoData.get('videoRenderer').get('videoId')
                videos.append([f'https://www.youtube.com/watch?v={videoId}', title])
            else:
                if numResults != len(searchData.get('contents').get('twoColumnSearchResultsRenderer').get('primaryContents').get('sectionListRenderer').get('contents')[0].get('itemSectionRenderer').get('contents'))-1:
                    numResults += 1

            c += 1
            break

    return videos

def download_mp3(name, url):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dl_path = os.path.join(dir_path, "music/")

    yt_options = {
        'format': 'bestaudio/best',
        'outtmpl': dl_path + '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    try: 
        with youtube_dl.YoutubeDL(yt_options) as ydl:
            ydl.download([url])
        print(f"{bcolors.HEADER}[{name}] downloaded{bcolors.ENDC}")

    except Exception as e:
        print(f"Error: {str(e)}")
        pass

def main():
    while True:
        title = input(f"{bcolors.FAIL}Enter song title:{bcolors.ENDC} ").replace(" ","+")
        videos = get_ids(title, numResults)
        for i in range(0, numResults):
            print(f"{bcolors.OKCYAN}{i+1}{bcolors.ENDC} - {bcolors.OKGREEN}{videos[i][1]}{bcolors.ENDC}")

        while True:
            option = input(f"{bcolors.FAIL}Song to download:{bcolors.ENDC} ")
            o = int(option)
            
            if o <= len(videos) and o > 0:
                break

        download_mp3(videos[o-1][1], videos[o-1][0])

if __name__ == '__main__':
    main()