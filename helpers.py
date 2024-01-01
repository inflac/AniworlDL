import os
import re
import time
import requests
import platform
import subprocess
from bs4 import BeautifulSoup
from Episode import Episode
import threading

#Color Codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

STOP_THREADS = False #Indicator showing if the program should get terminated
THREAD_DATA = {} #Dictionary to collect data about the downloading progress

data_update_mutex = threading.Lock() #Mutex to lock writing in THREAD_DATA

def get_time_formated(timeformat=None):
    if timeformat == None:
        return time.time()
    return time.strftime(timeformat)

def print_header():
    with open("header", "r") as header:
        for line in header.readlines():
            print(line, end="")
        print("")
    return

def parameter_checks(anime:str, season:int, episode:int, threads:int, path:str, proxy:dict):
    if proxy != None:
        req = requests.get("https://inflacsan.de", proxies=proxy)
        if req.status_code != 200:
            print(f"{RED}ERROR{RESET}: The given proxy returend status code: {BLUE}{req.status_code}{RESET} insted of {BLUE}200{RESET}.")
            exit(1)
        pass

    req = requests.get("https://aniworld.to/anime/stream/" + anime, proxies=proxy)
    if "messageAlert danger" in str(req.content):
        print(f"{RED}ERROR{RESET}: The name of the anime you provided is wrong. Please regard the anime naming schemea for this downloader.")
        exit(1)

    if threads > 5:
        print(f"{BLUE}INFO{RESET}: You are using a lot of threads.")
    
    if not os.path.isdir(path):
        print(f"{RED}ERROR{RESET}: The path you provided do not exist or is not a path to a folder.")
        exit(1)
    
    print(f'[{get_time_formated(timeformat="%H:%M")}] Parameter checks [{GREEN}Done{RESET}]')

def set_stop_indicator():
    global STOP_THREADS
    STOP_THREADS = True

def get_stop_indicator():
    global STOP_THREADS
    return STOP_THREADS

def update_download_data():
    global THREAD_DATA
    items = THREAD_DATA.items()
    for key, value in items:
        print(f"{key}: {value[1]}/{value[0]}, ", end="")
    print("", end="\r")
    
def get_episodes_links(anime=None, season="", episode="", proxy=None):
    episodes_elem = []

    url = "https://aniworld.to/anime/stream/" + anime + "/staffel-" + str(season)
    
    req = requests.get(url, proxies=proxy)

    soup = BeautifulSoup(req.content, 'html.parser')
    episodes = soup.find_all('tr', {'itemprop': 'episode'})

    for episode in episodes:
        episode_id = episode['data-episode-id']
        episode_name = episode.find('strong').text.strip()
        episode_num = episode.find('a').text.strip()
        episode_url = "https://aniworld.to/" + str(episode.find('a', itemprop='url')['href'])
        episodes_elem.append(Episode(episode_id, episode_name, episode_num, episode_url))
    return episodes_elem

def download_from_url(title:str, url:str, proxy:dict):
    extension = ".mp4"
    if url[-4:] != extension:
        extension = ".unkn"

    req = requests.get(url, stream=True, proxies=proxy)
    if req.status_code == 200:
        total_data_size = int(req.headers.get('content-length', 0))
        with open(title + extension, 'wb') as file:
            downloaded_data = 0
            for i,chunk in enumerate(req.iter_content(chunk_size=1024)):
                if get_stop_indicator():
                    file.close()
                    return False
                file.write(chunk)
                downloaded_data += len(chunk)
                data_update_mutex.acquire()
                THREAD_DATA[title]=[total_data_size,downloaded_data] #Dict, containing information (not threadsafe!)
                data_update_mutex.release()
                update_download_data()
            file.close()
            THREAD_DATA.pop(title)
    return True

def downloade_from_m3u8(title:str, path:str, m3u8_url:str):
    return False #TODO This function needs to be implemented 


def download_episode(episode, streamer, path:str, proxy:dict):
    print(f'[{get_time_formated(timeformat="%H:%M")}] Downloading episode: [{BLUE}{episode.episode_num}{RESET}] by streamer: [{BLUE}{streamer.name}{RESET}]')
    req = requests.get(streamer.url, proxies=proxy)
    if req.status_code != 200:
        print(f'[{RED}ERROR{RESET}] Requesting the episodes stream url returend a status code: {BLUE}{req.status_code}{RESET}')
        return False
    soup = BeautifulSoup(req.content, 'html.parser')

    if streamer.name == "VOE":
        VOE_PATTERN = re.compile(r"'hls': '(?P<url>.+)'")
        m3u8_url = VOE_PATTERN.search(req.content.decode('utf-8')).group("url")
        episode.set_m3u8_url(m3u8_url)
        streamer.set_m3u8_url(m3u8_url)
        if downloade_from_m3u8(episode.episode_num, path, m3u8_url):
            print(f'[{get_time_formated(timeformat="%H:%M")}] Episode: [{BLUE}{episode.episode_num}{RESET}] [{GREEN}Done{RESET}]')
            return True
        return False
    elif streamer.name == "Doodstream":
        pass # TODO implement a downloading logic
    elif streamer.name == "Vidoza":
        video_element = soup.find('source', {'type':'video/mp4'})
        if video_element:
            video_src = video_element['src']
            if download_from_url(episode.episode_num, video_src, proxy):
                print(f'[{get_time_formated(timeformat="%H:%M")}] Episode: [{BLUE}{episode.episode_num}{RESET}] [{GREEN}Done{RESET}]')
            return True
        else:
            print(f'[{RED}ERROR{RESET}] Video URL could not be found')
        return False
    elif streamer.name == "Streamtape":
        STREAMTAPE_PATTERN = re.compile(r'get_video\?id=[^&\'\s]+&expires=[^&\'\s]+&ip=[^&\'\s]+&token=[^&\'\s]+\'')
        video_src = STREAMTAPE_PATTERN.search(req.content.decode('utf-8'))
        if video_src != None:
            video_src = "https://" + streamer.name + ".com/" + video_src.group()[:-1]
            if download_from_url(episode.episode_num, video_src, proxy):
                print(f'[{get_time_formated(timeformat="%H:%M")}] Episode: [{BLUE}{episode.episode_num}{RESET}] [{GREEN}Done{RESET}]')
                return True
        else:
            print(f'[{RED}ERROR{RESET}] Video URL could not be found')
        return False
    else:
        print(f'[{RED}ERROR{RESET}] The Streamer: {BLUE}{streamer.name}{RESET} is not supported')
        return False
    return True