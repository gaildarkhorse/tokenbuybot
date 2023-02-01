# /usr
import songs
import requests
import time
import urllib3
import config
import os,json
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
chainIds={
    "ETH":1,
    "BSC":56
}

class BotAPI:

    def __init__(self, gid, data, r=requests.Session()):
        self.gid = gid
        self.data = data
        self.r = r
        self.pairs = []

    def get_tokeninfo(self):
        self.token_symbol = ""
        self.pairs = []
        params = {'groupId':str(self.gid),'tokenAddress': self.data["token_address"], "chainId":chainIds[self.data["chain"]]}
        print(params)
        print(json.dumps(params, indent = 4))
        self.response = self.r.post("https://tetrabotapi.cryptosnowprince.com/api/monitoringgroup/getPairs",  data=params , verify=False)

        res = self.response.json()
        print("get_pairs_response:", res)
        if self.response.status_code == 200:
            try:
                if res["code"]==0: self.pairs = res["pairs"]
            except KeyError:
                print("get_pairs : data error")
        else:
            print("get_pairs : fail")
        return self.pairs

    def stop(self):
        params = {'groupId':self.gid,'tokenAddress': self.data["token_address"], "chainId":chainIds[self.data["chain"]]}
        self.response = self.r.post("https://blocktestingto.com/api/monitoringgroup/stop", data=params, verify=False)
        print("stop_response:", self.response.json())
        if self.response.status_code == 200:
            return True
        return False
    
    def download_song(self, link):
        self.link = link
        self.response = self.r.get(
            f"{self.link}",  verify=False)
        # print("self.response",self.response)
        if self.response.status_code == 200:
            return self.response.content
        else:
            return False
