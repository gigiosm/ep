# -*- coding: utf-8 -*-

import sys
import os
import xbmcaddon
import xbmcgui
import xbmc
import json
import requests
import xbmcvfs
import xml.etree.ElementTree as ET


addon = xbmcaddon.Addon(id='script.365.epg.generator')
userpath = addon.getAddonInfo('profile')
custom_channels = xbmcvfs.translatePath("%s/custom_channels.txt" % userpath)
custom_channels_tm = xbmcvfs.translatePath("%s/custom_channels_tm.txt" % userpath)
custom_channels_o2 = xbmcvfs.translatePath("%s/custom_channels_o2.txt" % userpath)
custom_channels_mujtv = xbmcvfs.translatePath("%s/custom_channels_mujtv.txt" % userpath)
custom_channels_es = xbmcvfs.translatePath("%s/custom_channels_es.txt" % userpath)
custom_channels_stv = xbmcvfs.translatePath("%s/custom_channels_stv.txt" % userpath)
custom_channels_stvsk = xbmcvfs.translatePath("%s/custom_channels_stvsk.txt" % userpath)
custom_channels_mag = xbmcvfs.translatePath("%s/custom_channels_mag.txt" % userpath)
custom_channels_tvspiel = xbmcvfs.translatePath("%s/custom_channels_tvspiel.txt" % userpath)
custom_channels_ottplay = xbmcvfs.translatePath("%s/custom_channels_ottplay.txt" % userpath)
channels_select_path = xbmcvfs.translatePath(userpath + "/channels.json")
if not xbmcvfs.exists(userpath):
    xbmcvfs.mkdir(userpath)


def select():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    category = {"České": "CZ", "Slovenské": "SK", "Polské": "PL", "Německé": "DE", "Anglické": "EN", "Francouzské": "FR", "Maďarské": "HU", "Ruské": "RU", "Španělské": "ES", "Italské": "IT", "Ostatní": "", "T-Mobile TV GO": "TM", "Magio GO": "MAG", "O2 TV Sport": "O2", "můjTVprogram.cz": "MTV", "Eurosport": "ES", "SledovaniTV.cz": "STV", "SledovanieTV.sk": "STVSK", "TV Spiel": "SPIEL", "OTT Play": "OTT"}
    if category[sys.argv[1]] == "TM":
        params={"dsid": "c75536831e9bdc93", "deviceName": "Xiaomi Mi 11", "deviceType": "OTT_STB", "osVersion": "10", "appVersion": "3.7.0", "language": "CZ"}
        headers={"Host": "czgo.magio.tv", "authorization": "Bearer", "User-Agent": "okhttp/3.12.12", "content-type":  "application/json", "Connection": "Keep-Alive"}
        req = requests.post("https://czgo.magio.tv/v2/auth/init", params=params, headers=headers, verify=True).json()
        token = req["token"]["accessToken"]
        headers2={"Host": "czgo.magio.tv", "authorization": "Bearer " + token, "User-Agent": "okhttp/3.12.12", "content-type":  "application/json"}
        req1 = requests.get("https://czgo.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE", headers=headers2).json()["items"]
        tm_channels = {}
        for y in req1:
            name = y["channel"]["name"]
            id = str(y["channel"]["channelId"])
            tm_channels[name.replace(" HD", "")] = id
        channels = list(tm_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "MAG":
        params={"dsid": "c75536831e9bdc93", "deviceName": "Xiaomi Mi 11", "deviceType": "OTT_STB", "osVersion": "10", "appVersion": "3.7.0", "language": "SK"}
        headers={"Host": "skgo.magio.tv", "authorization": "Bearer", "User-Agent": "okhttp/3.12.12", "content-type":  "application/json", "Connection": "Keep-Alive"}
        req = requests.post("https://skgo.magio.tv/v2/auth/init", params=params, headers=headers, verify=True).json()
        token = req["token"]["accessToken"]
        headers2={"Host": "skgo.magio.tv", "authorization": "Bearer " + token, "User-Agent": "okhttp/3.12.12", "content-type":  "application/json"}
        req1 = requests.get("https://skgo.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE", headers=headers2).json()["items"]
        mag_channels = {}
        for y in req1:
            name = y["channel"]["name"]
            id = str(y["channel"]["channelId"])
            mag_channels[name.replace(" HD", "")] = id
        channels = list(mag_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "O2":
        o2_channels = {"O2TV Sport": "O2 Sport HD", "O2TV Fotbal": "O2 Fotbal HD", "O2TV Tenis": "O2 Tenis HD", "O2TV Sport1": "O2 Sport1 HD", "O2TV Sport2": "O2 Sport2 HD", "O2TV Sport3": "O2 Sport3 HD", "O2TV Sport4": "O2 Sport4 HD", "O2TV Sport5": "O2 Sport5 HD", "O2TV Sport6": "O2 Sport6 HD", "O2TV Sport7": "O2 Sport7 HD", "O2TV Sport8": "O2 Sport8 HD"}
        channels = list(o2_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "MTV":
        mujtv_channels = {'Skylink 7': '723', 'Stingray Classica': '233', 'Stingray iConcerts': '234', 'Stingray CMusic': '110', 'ORF1': '40', 'ORF2': '41', 'RTL': '49', 'RTL2': '50', 'Polsat': '39', 'TVP1': '37', 'TVP2': '38', 'Pro7': '174', 'SAT1': '52', 'Kabel1': '54', 'VOX': '53', 'ZDF': '393', 'ZDF Neo': '216', '3SAT': '46', 'SAT.1 GOLD': '408', 'Vixen': '892', 'Canal+ Sport': '1040'}
        channels = list(mujtv_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "ES":
        es_channels = {"Eurosport 3": "Eurosport3", "Eurosport 4": "Eurosport4", "Eurosport 5": "Eurosport5"}
        channels = list(es_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "STV":
        stv_channels = {}
        req = requests.get("http://felixtv.wz.cz/epg/channels.php").json()
        for x in req["channels"]:
            stv_channels[x["name"]] = x["id"]
        channels = list(stv_channels.keys())
#        sorted(channels)
    elif category[sys.argv[1]] == "STVSK":
        stvsk_channels = {}
        req = requests.get("http://felixtv.wz.cz/epg/channels_sk.php").json()
        for x in req["channels"]:
            stvsk_channels[x["name"]] = x["id"]
        channels = list(stvsk_channels.keys())
#        sorted(channels)
    elif category[sys.argv[1]] == "SPIEL":
        spiel_channels = {'Eurosport 1 (DE)': 'EURO', 'Eurosport 2 (DE)': 'EURO2', 'Sky Sport 1 (DE)': 'HDSPO', 'Sky Sport 2 (DE)': 'SHD2', 'Sky Sport Austria1': 'SPO-A', 'ORF Sport+': 'ORFSP'}
        channels = list(spiel_channels.keys())
        sorted(channels)
    elif category[sys.argv[1]] == "OTT":
        ottplay_channels = {'Penthouse Gold': '7:2777', 'Penthouse Quickies': '7:2779', 'Vivid Red': '7:2528', 'Super Tennis': 'ITbas:SuperTennis.it'}
        channels = list(ottplay_channels.keys())
        sorted(channels)
    else:
        channels = []
        html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ").text
        root = ET.fromstring(html)
        for i in root.iter('a'):
            if i.attrib["c"] == category[sys.argv[1]]:
                channels.append(i.find('n').text)
    if os.path.exists(channels_select_path):
        f = open(channels_select_path, "r").read()
        data = json.loads(f)
        try:
            ch = data[sys.argv[1].encode().decode("utf-8")][0]
            ch_preselect = []
            for i in ch:
                ch_preselect.append(channels.index(i))
        except:
            ch_preselect = []
    else:
        ch_preselect = []
        data = {}
    repair_channels = []
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    dialog = xbmcgui.Dialog()
    types = dialog.multiselect(sys.argv[1], channels, preselect=ch_preselect)
    if types is None:
        pass
    else:
        for index in types:
            repair_channels.append(channels[index])
        select_channels = []
        if category[sys.argv[1]] == "TM":
            for key, value in tm_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "MAG":
            for key, value in mag_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "O2":
            for key, value in o2_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "MTV":
            for key, value in mujtv_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "ES":
            for key, value in es_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "STV":
            for key, value in stv_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "STVSK":
            for key, value in stvsk_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "SPIEL":
            for key, value in spiel_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        elif category[sys.argv[1]] == "OTT":
            for key, value in ottplay_channels.items():
                if key in repair_channels:
                    select_channels.append(value)
        else:
            for i in root.iter('a'):
                if i.find('n').text in repair_channels:
                    select_channels.append(i.attrib["id"])

        ff = open(channels_select_path, "w")
        data[sys.argv[1].encode().decode("utf-8")] = [repair_channels, ",".join(select_channels)]
        json.dump(data, ff)
        ff.close()
        if category[sys.argv[1]] == "TM":
            c_path = custom_channels_tm
            id = data["T-Mobile TV GO"][1]
        elif category[sys.argv[1]] == "MAG":
            c_path = custom_channels_mag
            id = data["Magio GO"][1]
        elif category[sys.argv[1]] == "O2":
            c_path = custom_channels_o2
            id = data["O2 TV Sport"][1]
        elif category[sys.argv[1]] == "MTV":
            c_path = custom_channels_mujtv
            id = data["můjTVprogram.cz"][1]
        elif category[sys.argv[1]] == "ES":
            c_path = custom_channels_es
            id = data["Eurosport"][1]
        elif category[sys.argv[1]] == "STV":
            c_path = custom_channels_stv
            id = data["SledovaniTV.cz"][1]
        elif category[sys.argv[1]] == "STVSK":
            c_path = custom_channels_stvsk
            id = data["SledovanieTV.sk"][1]
        elif category[sys.argv[1]] == "SPIEL":
            c_path = custom_channels_tvspiel
            id = data["TV Spiel"][1]
        elif category[sys.argv[1]] == "OTT":
            c_path = custom_channels_ottplay
            id = data["OTT Play"][1]
        else:
            c_path = custom_channels
            id = []
            for key, value in data.items():
                if key != "T-Mobile TV GO" and key != "Magio GO" and key != "O2 TV Sport" and key != "můjTVprogram.cz" and key != "Eurosport" and key != "SledovaniTV.cz" and key != "SledovanieTV.sk" and key != "TV Spiel" and key != "OTT Play":
                    if value[1] != "":
                        id.append(value[1])
            id = ",".join(id)
        fff = open(c_path, "w")
        fff.write(id)
        fff.close()


if __name__ == "__main__":
    select()