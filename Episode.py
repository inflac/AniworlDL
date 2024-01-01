from bs4 import BeautifulSoup
import requests

from Streamer import Streamer

class Episode:
    def __init__(self, episode_id, name, episode_num, url):
        self.episode_id = episode_id
        self.name = name
        self.episode_num = episode_num
        self.url = url
        self.streaming_services = self.get_streamers()
        self.m3u8_url = None


    def get_streamers(self):
        content = requests.get(self.url).content
        soup = BeautifulSoup(content, 'html.parser')
        streamers = soup.find_all('li', class_='col-md-3')

        streamers_elem = []
        for streamer in streamers:
            if streamer['data-lang-key'] == "1":
                link_id = streamer['data-link-id']
                streaming_service = streamer.find('h4').text.strip()
                link_target = streamer['data-link-target']
                streamers_elem.append(Streamer(streaming_service, link_target, link_id))
        return streamers_elem

    def set_m3u8_url(self, m3u8_url:str):
        self.m3u8_url = m3u8_url


        