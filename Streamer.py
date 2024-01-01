class Streamer:
    def __init__(self, name:str, red_url:str, id:int):
        self.name = name
        self.red_url = red_url
        self.id = id
        self.url = self.construct_episode_url()
        self.m3u8_url = None

    def construct_episode_url(self):
        return "https://aniworld.to" + str(self.red_url)

    def set_m3u8_url(self, m3u8_url:str):
        self.m3u8_url = m3u8_url



