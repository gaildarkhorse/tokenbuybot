# /usr
import songs
import requests
import time
import urllib3
import config
import os
# from mutagen.mp3 import MP3

# def mutagen_length(path):
#     try:
#         audio = MP3(path)
#         length = audio.info.length
#         return length
#     except:
#         return None
# import vk_audio, vk_api
# from vk_api import audio
urllib3.disable_warnings()


class SongsDownloader:

    def __init__(self, search_value="all", r=requests.Session()):

        self.search_value = search_value
        self.search_field = "all" if search_value=="all" else config.search_field
        self.r = r
        # login='18328400708'; password='Radiopass1##'
        # vk_session = vk_api.VkApi(login=login, password=password)
        # vk_session.auth(token_only=False)
        # vk_session.get_api()
        # self.vk_aud = audio.VkAudio(vk_session)

    def get_songs_list(self, count):

        self.count = count
        print("searchfield:", self.search_field, "searchvalue:", self.search_value)
        headers = {
            'user-agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}

        params = {'searchfield': self.search_field, "searchvalue":self.search_value, "password": "nftmarketplace"}

        # self.response = songs.songlist
        self.response = self.r.post("https://radioreum.com/api/item/musics",
                                    data=params, verify=False)
        # print("response:", self.response.json())
        if self.response.status_code == 200:
            try:
                formated_list = []
                urls_list = []
                without_formating = []
                i = 1
                for item in self.response.json()['data']:
                    if i == self.count + 1:
                        i = 1

                    if len(item['songTitle']) > 50 or len(item['artist']) > 50:
                        continue
                    item_url = f"https://radioreum.com/uploads/{item['url']}"
                    # duration = os.path.getsize(item_url)
                    # print("duration", duration)
                    formated_list.append(
                        # f"<b>{i}</b>. {item['songTitle']} - {item['artist']},   {config.CATEGORIES[item['category']]} <em>{int(item['duration']/60)}:{item['duration']%60}</em>")
                        f"<b>{i}</b>. {item['songTitle']} - {item['artist']},   {config.CATEGORIES[item['category']]}")
                    
                    urls_list.append(item_url)
                    without_formating.append(item)
                    i += 1

                def f(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]

                def u(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]

                def w(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]
                print("result ok")
                return f(formated_list), u(urls_list), w(without_formating)

            except KeyError:
                print("result: error")
                return "NoSongs", "NoSongs"
        else:
            print("result: false")
            return False

    def download_song(self, link):
        self.link = link
        print("link", link)
        headers = {
            'user-agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
        self.response = self.r.get(
            f"{self.link}",  verify=False)
        # print("self.response",self.response)
        if self.response.status_code == 200:
            return self.response.content

        else:
            return False
