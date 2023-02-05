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
    "BSC":56,
    "BSCTEST":97
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
        if self.data["chain"]=="":
            print("get_pairs : not initialized")
            return self.pairs
        # print(self.data)
        params = {'groupId':str(self.gid),'tokenAddress': self.data["token_address"], "chainId":chainIds[self.data["chain"]]}
        print(params)
        # print(json.dumps(params, indent = 4))
        
        self.response = self.r.post("https://tetra.tg.api.cryptosnowprince.com/api/getPairs",  data=params , verify=False)

        
        print("get_pairs_response:", self.response)
        if self.response.status_code == 200:
            try:
                res = self.response.json()
                print(res)
                self.pairs = res["pairs"]
            except KeyError:
                print("get_pairs : data error")
        else:
            print("get_pairs : fail")
        return self.pairs

    def stop(self):
        # if self.data["chain"]=="":
        #     print("stop_comp : not initialized")
        #     return False
        params = {'groupId':self.gid}
        self.response = self.r.post("https://tetra.tg.api.cryptosnowprince.com/api/stop", data=params, verify=False)
        if self.response.status_code == 200:
            return True
        return False
    def setSelectedPair(self):
        params = {'groupId':self.gid,'tokenAddress': self.data["token_address"], "chainId":chainIds[self.data["chain"]], "selectedPair":self.data["pair_address"], "alt_token_name": self.data["alt_token_name"]}
        self.response = self.r.post("https://tetra.tg.api.cryptosnowprince.com/api/setSelectedPair", data=params, verify=False)
        if self.response.status_code == 200:
            return True
        return False

    
    def start(self):
        g_data = self.data
        params = {"groupId":self.gid,'tokenAddress': self.data["token_address"], "chainId":chainIds[self.data["chain"]], "compType":g_data["comp_type"], "pairAddress":g_data["pair_address"], "tokenName":g_data['token_name'], "altTokenName":g_data['alt_token_name'], "minBuy":g_data[g_data['comp_type']]['min_buy']}
        # print(params)
        self.response = self.r.post("https://tetra.tg.api.cryptosnowprince.com/api/start",  data=params , verify=False)
        print("start_response:", self.response)

    
    def download_song(self, link):
        self.link = link
        self.response = self.r.get(
            f"{self.link}",  verify=False)
        # print("self.response",self.response)
        if self.response.status_code == 200:
            return self.response.content
        else:
            return False
