# -*- coding: utf-8 -*-

import sys
import os
import xbmcaddon
import xbmcgui
import xbmc
import xbmcvfs
from datetime import datetime, timedelta, date
import xml.etree.ElementTree as ET
import unicodedata
import time
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
try:
    from resources.lib import xmltv
except:
    import xmltv


addon = xbmcaddon.Addon(id='script.365.epg.generator')
download_path = addon.getSetting("folder")
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
temp_epg = xbmcvfs.translatePath("%s/epg.xml" % userpath)
custom_names_path = xbmcvfs.translatePath("%s/custom_names.txt" % userpath)
now = datetime.now()
local_now = now.astimezone()
TimeShift = " " + str(local_now)[-6:].replace(":", "")
TimeShift1 = TimeShift[:3] + str(int(TimeShift[3]) -1) + TimeShift[4:]
W = xmltv.Writer(encoding="utf-8", source_info_url="http://www.funktronics.ca/python-xmltv", source_info_name="Funktronics", generator_info_name="python-xmltv", generator_info_url="http://www.funktronics.ca/python-xmltv")


custom_names = []
if addon.getSetting("notice") == "true" and addon.getSetting("dialog") == "true":
    DLG = True
else:
    DLG = False


try:
    f = open(custom_names_path, "r", encoding="utf-8").read().splitlines()
    for x in f:
        x = x.split("=")
        custom_names.append((x[0], x[1]))
except:
    pass


if addon.getSetting("custom_names") == "true":
    CN = True
else:
    CN = False
if addon.getSetting("diacritics") == "false":
    DC = False
else:
    DC = True


def replace_names(value):
    if CN == True:
        for v in custom_names:
            if v[0] == value:
                value = v[1]
    return value


def encode(string):
    if DC == False:
        string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
    return string


def notice(text, type):
    if addon.getSetting("notice") == "true" and addon.getSetting("dialog") == "false":
        if type == 0:
            xbmcgui.Dialog().notification("365 EPG Generator",text, xbmcgui.NOTIFICATION_INFO, 4000, sound = False)
        else:
            xbmcgui.Dialog().notification("365 EPG Generator",text, xbmcgui.NOTIFICATION_ERROR, 4000, sound = True)


def restart_pvr():
    if addon.getSetting("restart_pvr") == "true":
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid": "pvr.iptvsimple","enabled":false}}')
        time.sleep(2)
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid": "pvr.iptvsimple","enabled":true}}')
        if addon.getSetting("play_pvr") == "true":
            time.sleep(5)
            if addon.getSetting("pvr_type") == "0":
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"playpvrtv"},"id":1}')
            else:
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"playpvrradio"},"id":1}')


def get_stvsk_programmes(stv_ids, d, d_b):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("SledovanieTV.sk", "")
        dialog.update(0, "SledovanieTV.sk", "Stahování dat...")
    if d_b > 7:
        d_b = 7
    if d > 15:
        d = 15
    stv_channels = {}
    req = requests.get("http://felixtv.wz.cz/epg/channels_sk.php").json()
    for x in req["channels"]:
        stv_channels[x["id"]] = x["name"]
    if stv_ids == "":
        stv_id = "".join('{},'.format(k) for k in stv_channels.keys())[:-1]
    else:
        stv_id = stv_ids
    for k, v in stv_channels.items():
        if k in stv_id.split(","):
            W.addChannel({'display-name': [(replace_names(v), u'cs')], 'id': 'stvsk-' + k,'icon': [{'src': 'https://sledovanietv.sk/cache/biglogos/' + k + '.png'}]})
    now = datetime.now()
    st = 1
    try:
        for i in range(d_b*-1, d):
            next_day = now + timedelta(days = i)
            date_from = next_day.strftime("%Y-%m-%d")
            date_ = next_day.strftime("%d.%m.%Y")
            req = requests.get("http://felixtv.wz.cz/epg/stv_sk.php?ch=" + stv_id + "&d=" + date_from).json()["channels"]
            for k in req.keys():
                for x in req[k]:
                    programm = {'channel': "stvsk-" + k, 'start': x["startTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TimeShift, 'stop': x["endTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TimeShift, 'title': [(x["title"], u'')], 'desc': [(x["description"], u'')]}
                    try:
                        icon = x["poster"]
                    except:
                        icon = None
                    if icon != None:
                        programm['icon'] = [{"src": icon}]
                    try:
                        genres = []
                        for g in x["genres"]:
                            genres.append((g["name"], u''))
                    except:
                        genres = []
                    if genres != []:
                        programm['category'] = genres
                    W.addProgramme(programm)
            per = int(d_b) + int(d)
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "SledovanieTV.sk", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "SledovanieTV.sk", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("SledovanieTV.sk","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)
        

def get_stv_programmes(stv_ids, d, d_b):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("SledovaniTV.cz", "")
        dialog.update(0, "SledovaniTV.cz", "Stahování dat...")
    if d_b > 7:
        d_b = 7
    if d > 15:
        d = 15
    stv_channels = {}
    try:
        req = requests.get("http://felixtv.wz.cz/epg/channels.php").json()
        for x in req["channels"]:
            stv_channels[x["id"]] = x["name"]
        if stv_ids == "":
            stv_id = "".join('{},'.format(k) for k in stv_channels.keys())[:-1]
        else:
            stv_id = stv_ids
        for k, v in stv_channels.items():
            if k in stv_id.split(","):
                W.addChannel({'display-name': [(replace_names(v), u'cs')], 'id': 'stv-' + k,'icon': [{'src': 'https://sledovanitv.cz/cache/biglogos/' + k + '.png'}]})
        now = datetime.now()
        st = 1
        for i in range(d_b*-1, d):
            next_day = now + timedelta(days = i)
            date_from = next_day.strftime("%Y-%m-%d")
            date_ = next_day.strftime("%d.%m.%Y")
            req = requests.get("http://felixtv.wz.cz/epg/stv.php?ch=" + stv_id + "&d=" + date_from).json()["channels"]
            for k in req.keys():
                for x in req[k]:
                    programm = {'channel': "stv-" + k, 'start': x["startTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TimeShift, 'stop': x["endTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TimeShift, 'title': [(x["title"], u'')], 'desc': [(x["description"], u'')]}
                    try:
                        icon = x["poster"]
                    except:
                        icon = None
                    if icon != None:
                        programm['icon'] = [{"src": icon}]
                    try:
                        genres = []
                        for g in x["genres"]:
                            genres.append((g["name"], u''))
                    except:
                        genres = []
                    if genres != []:
                        programm['category'] = genres
                    W.addProgramme(programm)
            per = int(d_b) + int(d)
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "SledovaniTV.cz", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "SledovaniTV.cz", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        session.close()
        if DLG == True:
            dialog.close()
        channels, programmes = [], []
        xbmcgui.Dialog().notification("SledovaniTV.cz","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_ott_play_programmes(ids):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("OTT Play", "")
        dialog.update(0, "OTT Play", "Stahování dat...")
    channels = []
    f = {"7:2777": "fox-tv", "7:2779": "fox-tv", "7:2528": "fox-tv", "ITbas:SuperTennis.it": "korona"}
    ids_ = ids.split(",")
    c = {'display-name': [(replace_names('Penthouse Gold'), u'cs')], 'id': '7:2777','icon': [{'src': 'http://pics.cbilling.pw/streams/penthouse1-hd.png'}]}, {'display-name': [(replace_names('Penthouse Quickies'), u'cs')], 'id': '7:2779','icon': [{'src': 'http://pics.cbilling.pw/streams/penthouse2-hd.png'}]}, {'display-name': [(replace_names('Vivid Red'), u'cs')], 'id': '7:2528','icon': [{'src': 'http://pics.cbilling.pw/streams/vivid-red-hd.png'}]}, {'display-name': [(replace_names('Super Tennis'), u'cs')], 'id': 'ITbas:SuperTennis.it','icon': [{'src': 'https://guidatv.sky.it/logo/5246supertennishd_Light_Fit.png?checksum=13f5cbb1646d848fde3af6fccba8dd4c'}]}
    for x in c:
        if x["id"] in ids_:
            W.addChannel(x)
    programmes = []
    headers = {"User-Agent": "Mozilla/5.0 (Linux; U; Android 12; cs-cz; Xiaomi 11 Lite 5G NE Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.116 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.16.3.1-gn", "Host": "epg.ott-play.com", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Connection": "keep-alive"}
    try:
        for id in ids_:
            r = requests.get("http://epg.ott-play.com/php/show_prog.php?f=" + f[id] + "/epg/" + id + ".json", headers = headers)
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find_all('table')[0]
            tr = table.find_all("tr")
            data = []
            for td in tr:
               cols = td.find_all("td")
               cols = [ele.text.strip() for ele in cols]
               data.append([ele for ele in cols if ele])
            for d in data[1:]:
                dat = d[0].split("/")
                dat = dat[2] + dat[1] + dat[0]
                ts = d[1][:5].replace(":", "") + "00"
                te = d[1][6:11].replace(":", "") + "00"
                timestart = dat + ts
                timeend = dat + te
                title = d[2]
                try:
                    if "|" in d[3]:
                        descr = d[3].split(" | ")[1][2:]
                    else:
                        descr = d[3]
                except:
                    descr = ""
                W.addProgramme({"channel": id, "start": timestart + TimeShift, "stop": timeend + TimeShift, "title": [(title, "")], "desc": [(descr, u'')]})
        if DLG == True:
            dialog.update(100, "OTT Play", "Stahování dat...")
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("OTT Play","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_tv_spiel_programmes(ids, d, d_b):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("TV Spiel", "")
        dialog.update(0, "TV Spiel", "Stahování dat...")
    ids = ids.split(",")
    if d_b > 7:
        d_b = 7
    if d > 14:
        d = 14
    channels = []
    programmes = []
    ids_ = {'display-name': [(replace_names('Eurosport 1 (DE)'), u'cs')], 'id': 'EURO','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/EURO.png'}]}, {'display-name': [(replace_names('Eurosport 2 (DE)'), u'cs')], 'id': 'EURO2','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/EURO2.png'}]}, {'display-name': [(replace_names('Sky Sport 1 (DE)'), u'cs')], 'id': 'HDSPO','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/HDSPO.png'}]}, {'display-name': [(replace_names('Sky Sport 2 (DE)'), u'cs')], 'id': 'SHD2','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/SHD2.png'}]}, {'display-name': [(replace_names('Sky Sport Austria1'), u'cs')], 'id': 'SPO-A','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/SPO-A.png'}]}, {'display-name': [(replace_names('ORF Sport+'), u'cs')], 'id': 'ORFSP','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/ORFSP.png'}]}
    for x in ids_:
        if x["id"] in ids:
            W.addChannel(x)
    st = 1
    now = datetime.now()
    try:
        for x in range(d_b*-1, d):
            next_day = now + timedelta(days = x)
            date_ = next_day.strftime("%d.%m.%Y")
            date = next_day.strftime("%Y-%m-%d")
            for y in ids:
                html = requests.get("https://live.tvspielfilm.de/static/broadcast/list/" + y + "/" + date).json()
                for x in html:
                    start = time.strftime('%Y%m%d%H%M%S', time.localtime(int(x['timestart'])))
                    stop = time.strftime('%Y%m%d%H%M%S', time.localtime(int(x['timeend'])))
                    try:
                        desc = x['text']
                    except:
                        desc = ""
                    programm = {"channel": y, "start": str(start) + TimeShift, "stop": str(stop) + TimeShift, "title": [(x['title'], "")], "desc": [(desc, u'')]}
                    try:
                        icon = x["images"][0]["size2"]
                    except:
                        icon = None
                    if icon != None:
                        programm['icon'] = [{"src": icon}]
                    W.addProgramme(programm)
            per = int(d_b) + int(d)
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "TV Spiel", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "TV Spiel", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("TV Spiel","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_muj_tv_programmes(ids, d, d_b):
    ids = ids.split(",")
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("můjTVprogram.cz", "")
        dialog.update(0, "můjTVprogram.cz", "Stahování dat...")
    if d_b > 1:
        d_b = 1
    if d > 10:
        d = 10
    channels = []
    programmes = []
    ids_ = {'723': '723-skylink-7', '233': '233-stingray-classica', '234': '234-stingray-iconcerts', '110': '110-stingray-cmusic', '40': '40-orf1', '41': '41-orf2', '49': '49-rtl', '50': '50-rtl2', '39': '39-polsat', '37': '37-tvp1', '38': '38-tvp2', '174': '174-pro7', '52': '52-sat1', '54': '54-kabel1', '53': '53-vox', '393': '393-zdf', '216': '216-zdf-neo', '46': '46-3sat', '408': '408-sat1-gold', '892': '892-vixen', '1040': '1040-canal+sport'}
    c = {'display-name': [(replace_names('Skylink 7'), u'cs')], 'id': '723-skylink-7','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ac6c69625699eaecc9b39f7ea4d69b8c&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray Classica'), u'cs')], 'id': '233-stingray-classica','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=661af53f8f3b997611c29f844c7006fd&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray iConcerts'), u'cs')], 'id': '234-stingray-iconcerts','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=99c87946872c81f46190c77af7cd1d89&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray CMusic'), u'cs')], 'id': '110-stingray-cmusic','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=b323f2ad3200cb938b43bed58dd8fbf9&amp;p2=80'}]}, {'display-name': [(replace_names('ORF1'), u'cs')], 'id': '40-orf1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=422162d3082a84fc97a7fb9b3ad6823f&amp;p2=80'}]}, {'display-name': [(replace_names('ORF2'), u'cs')], 'id': '41-orf2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=477dcc38e54309f5db7aec56b62b4cdf&amp;p2=80'}]}, {'display-name': [(replace_names('RTL'), u'cs')], 'id': '49-rtl','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=7cb9005e66956c56fd0671ee79ee2471&amp;p2=80'}]}, {'display-name': [(replace_names('RTL2'), u'cs')], 'id': '50-rtl2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=418e0d04529ea3aaa2bc2c925ddf5982&amp;p2=80'}]}, {'display-name': [(replace_names('Polsat'), u'cs')], 'id': '39-polsat','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=f54e290782e8352303cfe43ce949d339&amp;p2=80'}]}, {'display-name': [(replace_names('TVP1'), u'cs')], 'id': '37-tvp1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=770431539d1fa662f705c1c05a0dd943&amp;p2=80'}]}, {'display-name': [(replace_names('TVP2'), u'cs')], 'id': '38-tvp2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e2ce4065f27ce199f7613f38878cef72&amp;p2=80'}]}, {'display-name': [(replace_names('Pro7'), u'cs')], 'id': '174-pro7','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e23a7fb8caff9ff514f254c43a39d9b6&amp;p2=80'}]}, {'display-name': [(replace_names('SAT1'), u'cs')], 'id': '52-sat1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=97dd916e0164fff141065c3fba71c291&amp;p2=80'}]}, {'display-name': [(replace_names('Kabel1'), u'cs')], 'id': '54-kabel1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=be6dc88dd3c1c243ba4f28cccb8f1d34&amp;p2=80'}]}, {'display-name': [(replace_names('VOX'), u'cs')], 'id': '53-vox','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=d2c68d2b145a5f2e20e5c05c20a9679e&amp;p2=80'}]}, {'display-name': [(replace_names('ZDF'), u'cs')], 'id': '393-zdf','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=dad48d516fbdb30321564701cc3faa04&amp;p2=80'}]}, {'display-name': [(replace_names('ZDF Neo'), u'cs')], 'id': '216-zdf-neo','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=cd5b8935893b0e4cde41bc3720435f14&amp;p2=80'}]}, {'display-name': [(replace_names('3SAT'), u'cs')], 'id': '46-3sat','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=58d350c6065d9355a52c6dbc3b31b185&amp;p2=80'}]}, {'display-name': [(replace_names('SAT.1 GOLD'), u'cs')], 'id': '408-sat1-gold','icon': [{'src': ''}]}, {'display-name': [(replace_names('Vixen'), u'cs')], 'id': '892-vixen','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=4499ebafb26a915859febcb4306703ca&amp;p2=80'}]}, {'display-name': [(replace_names('Canal+ Sport'), u'cs')], 'id': '1040-canal+sport','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ab73879fdf9b10e1deb0224bfbb3cfd8&amp;p2=80'}]}
    for x in c:
        if x["id"].split("-")[0] in ids:
            W.addChannel(x)
    now = datetime.now()
    st = 1
    try:
        for x in range(d_b*-1, d):
            next_day = now + timedelta(days = x)
            date_ = next_day.strftime("%d.%m.%Y")
            for y in ids:
                html = requests.post("https://services.mujtvprogram.cz/tvprogram2services/services/tvprogrammelist_mobile.php", data = {"channel_cid": y, "day": str(x)}).content
                root = ET.fromstring(html)
                for i in root.iter("programme"):
                    W.addProgramme({"channel": ids_[y],  "start": time.strftime('%Y%m%d%H%M%S', time.localtime(int(i.find("startDateTimeInSec").text))) + TimeShift, "stop": time.strftime('%Y%m%d%H%M%S', time.localtime(int(i.find("endDateTimeInSec").text))) + TimeShift, "title": [(i.find("name").text, "")], "desc": [(i.find("shortDescription").text, "")]})
            per = int(d_b) + int(d)
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "můjTVprogram.cz", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "můjTVprogram.cz", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("můjTVprogram.cz","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_eurosport_programmes(es):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("Eeurosport", "")
        dialog.update(0, "Eeurosport", "Stahování dat...")
    channelKeys = es.split(",")
    params = ""
    for channelKey in channelKeys:
        params = params + ("&channelKey=" + quote(channelKey))
    programmes = []
    st = 1
    try:
        for i in range(int(addon.getSetting("num_days_back"))*-1, int(addon.getSetting("num_days"))):
            next_day = datetime.combine(date.today(), datetime.min.time()) + timedelta(days = i)
            date_ = next_day.strftime("%d.%m.%Y")
            to_day = next_day  + timedelta(minutes = 1439)
            dt_from = int(time.mktime(next_day.timetuple()))
            dt_to = int(time.mktime(to_day.timetuple()))
            url = "https://api.o2tv.cz/unity/api/v1/epg/depr/?forceLimit=true&limit=500" + params + "&from=" + str(dt_from*1000) + "&to=" + str(dt_to*1000)
            req = requests.get(url).json()
            for it in req["epg"]["items"]:
                ch_name= it["channel"]["name"].replace(" HD", "").replace(" ", "-").lower()
                for e in it["programs"]:
                    name = e["name"]
                    start = datetime.fromtimestamp(int(e["start"])/1000).strftime('%Y%m%d%H%M%S')
                    stop = datetime.fromtimestamp(int(e["end"])/1000).strftime('%Y%m%d%H%M%S')
                    if e["npvr"] == True:
                        req = requests.get("https://api.o2tv.cz/unity/api/v1/programs/" + str(e["epgId"]) + "/").json()
                        try:
                            desc = req["shortDescription"]
                        except:
                            desc = ""
                        W.addProgramme({"channel": ch_name, "start": start + TimeShift, "stop": stop + TimeShift, "title": [(name, "")], "desc": [(desc, u'')]})
                    else:
                        W.addProgramme({"channel": ch_name, "start": start + TimeShift, "stop": stop + TimeShift, "title": [(name, "")]})
            per = int(int(addon.getSetting("num_days_back")) + int(addon.getSetting("num_days")))
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "Eurosport", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "Eurosport", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("Eurosport","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_o2_programmes(o2):
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create("O2 TV Sport", "")
        dialog.update(0, "O2 TV Sport", "Stahování dat...")
    channelKeys = o2.split(",")
    params = ""
    for channelKey in channelKeys:
        params = params + ("&channelKey=" + quote(channelKey))
    programmes = []
    st = 1
    try:
        for i in range(int(addon.getSetting("num_days_back"))*-1, int(addon.getSetting("num_days"))):
            next_day = datetime.combine(date.today(), datetime.min.time()) + timedelta(days = i)
            date_ = next_day.strftime("%d.%m.%Y")
            to_day = next_day  + timedelta(minutes = 1439)
            dt_from = int(time.mktime(next_day.timetuple()))
            dt_to = int(time.mktime(to_day.timetuple()))
            url = "https://api.o2tv.cz/unity/api/v1/epg/depr/?forceLimit=true&limit=500" + params + "&from=" + str(dt_from*1000) + "&to=" + str(dt_to*1000)
            req = requests.get(url).json()
            for it in req["epg"]["items"]:
                ch_name= it["channel"]["name"].replace(" HD", "").replace(" ", "-").lower()
                for e in it["programs"]:
                    name = e["name"]
                    start = datetime.fromtimestamp(int(e["start"])/1000).strftime('%Y%m%d%H%M%S')
                    stop = datetime.fromtimestamp(int(e["end"])/1000).strftime('%Y%m%d%H%M%S')
                    if e["npvr"] == True:
                        req = requests.get("https://api.o2tv.cz/unity/api/v1/programs/" + str(e["epgId"]) + "/").json()
                        try:
                            desc = req["shortDescription"]
                        except:
                            desc = ""
                        W.addProgramme({"channel": ch_name, "start": start + TimeShift, "stop": stop + TimeShift, "title": [(name, "")], "desc": [(desc, u'')]})
                    else:
                        W.addProgramme({"channel": ch_name, "start": start + TimeShift, "stop": stop + TimeShift, "title": [(name, "")]})
            per = int(int(addon.getSetting("num_days_back")) + int(addon.getSetting("num_days")))
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, "O2 TV Sport", date_)
            st += 1
        if DLG == True:
            dialog.update(100, "O2 TV Sport", date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification("O2 TV Sport","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def get_tm_programmes(tm_ids, d, d_b, lng):
    if lng == "cz":
        prfx = "tm-"
        title_ = 'T-Mobile TV GO'
    else:
        prfx = "mag-"
        title_ = 'Magio GO'
    st = 1
    dialog = xbmcgui.DialogProgressBG()
    if DLG == True:
        dialog.create(title_, "")
        dialog.update(0, title_, "Stahování dat...")
    if d > 10:
        d = 10
    tm_ids_list = tm_ids.split(",")
    programmes2 = []
    try:
        params={"dsid": "c75536831e9bdc93", "deviceName": "Xiaomi Mi 11", "deviceType": "OTT_STB", "osVersion": "10", "appVersion": "3.7.0", "language": lng.upper()}
        headers={"Host": lng + "go.magio.tv", "authorization": "Bearer", "User-Agent": "okhttp/3.12.12", "content-type":  "application/json", "Connection": "Keep-Alive"}
        req = requests.post("https://" + lng + "go.magio.tv/v2/auth/init", params=params, headers=headers, verify=True).json()
        token = req["token"]["accessToken"]
        headers2={"Host": lng + "go.magio.tv", "authorization": "Bearer " + token, "User-Agent": "okhttp/3.12.12", "content-type":  "application/json"}
        req1 = requests.get("https://" + lng + "go.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE", headers=headers2).json()["items"]
        channels2 = []
        ids = ""
        tvch = {}
        if lng == "cz":
            tvch["Šlágr Muzika"] = "tm-6043-slagr-original"
            tvch["Šlágr 2 HD"] = "tm-4528-slagr-muzika"
            tvch["Trojka HD"] = "tm-4516-:24"
        else:
            tvch["Šlágr Muzika"] = "mag-6043-slagr-original"
            tvch["Šlágr 2 HD"] = "mag-4528-slagr-muzika"
#            tvch["Trojka HD"] = "mag-4516-:24"
        for y in req1:
            id = str(y["channel"]["channelId"])
            if tm_ids_list == [""]:
                name = y["channel"]["name"]
                logo = str(y["channel"]["logoUrl"])
                ids = ids + "," + id
                tm = str(ids[1:])
                tvch[name] = prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-")
                W.addChannel(({"display-name": [(name.replace(" HD", ""), u"cs")], "id": prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-"), "icon": [{"src": logo}]}))
            else:
                if id in tm_ids_list:
                    name = y["channel"]["name"]
                    logo = str(y["channel"]["logoUrl"])
                    ids = ids + "," + id
                    tm = str(ids[1:])
                    tvch[name] = prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-")
                    W.addChannel(({"display-name": [(name.replace(" HD", ""), u"cs")], "id": prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-"), "icon": [{"src": logo}]}))
        now = datetime.now()
        for i in range(d_b*-1, d):
            next_day = now + timedelta(days = i)
            back_day = (now + timedelta(days = i)) - timedelta(days = 1)
            date_to = next_day.strftime("%Y-%m-%d")
            date_from = back_day.strftime("%Y-%m-%d")
            date_ = next_day.strftime("%d.%m.%Y")
            req = requests.get("https://" + lng + "go.magio.tv/v2/television/epg?filter=channel.id=in=(" + tm + ");endTime=ge=" + date_from + "T23:00:00.000Z;startTime=le=" + date_to + "T23:59:59.999Z&limit=" + str(len(tvch)) + "&offset=0&lang=" + lng.upper(), headers=headers2).json()["items"]
            for x in range(0, len(req)):
                for y in req[x]["programs"]:
                    channel = y["channel"]["name"]
                    start_time = y["startTime"].replace("-", "").replace("T", "").replace(":", "")
                    stop_time = y["endTime"].replace("-", "").replace("T", "").replace(":", "")
                    title = y["program"]["title"]
                    desc = y["program"]["description"]
                    epi = y["program"]["programValue"]["episodeId"]
                    if epi != None:
                        title = title + " (" + epi + ")"
                    year = y["program"]["programValue"]["creationYear"]
                    try:
                        subgenre = y["program"]["programCategory"]["subCategories"][0]["desc"]
                    except:
                        subgenre = ''
                    try:
                        genre = [(y["program"]["programCategory"]["desc"], u''), (subgenre, u'')]
                    except:
                        genre = None
                    try:
                        icon = y["program"]["images"][0]
                    except:
                        icon = None
                    try:
                        directors = []
                        for dr in y["program"]["programRole"]["directors"]:
                            directors.append(dr["fullName"])
                    except:
                        directors = []
                    try:
                        actors = []
                        for ac in y["program"]["programRole"]["actors"]:
                            actors.append(ac["fullName"])
                    except:
                        actors = []
                    try:
                        programm = {'channel': tvch[channel], 'start': start_time + TimeShift, 'stop': stop_time + TimeShift, 'title': [(title, u'')], 'desc': [(desc, u'')]}
                        if year != None:
                            programm['date'] = year
                        if genre != None:
                            programm['category'] = genre
                        if icon != None:
                            programm['icon'] = [{"src": icon}]
                        if directors != []:
                            programm['credits'] = {"director": directors}
                            if actors != []:
                                programm['credits'] = {"director": directors, "actor": actors}
                        if actors != []:
                            programm['credits'] = {"actor": actors}
                            if directors != []:
                                programm['credits'] = {"actor": actors, "director": directors}
                        W.addProgramme(programm)
                    except:
                        pass
            per = int(int(d) + int(d_b))
            percent = int((float(st*100) / per))
            if DLG == True:
                dialog.update(percent, title_, date_)
            st += 1
        if DLG == True:
            dialog.update(100, title_, date_)
            time.sleep(0.5)
            dialog.close()
    except:
        if DLG == True:
            dialog.close()
        xbmcgui.Dialog().notification(title_,"Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


class Get_channels_sms:

    def __init__(self):
        self.channels = []
        self.dialog = xbmcgui.DialogProgressBG()
        if DLG == True:
            self.dialog.create("TV.SMS.cz", "")
            self.dialog.update(0, "TV.SMS.cz","Stahování dat...")
        headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
        try:
            self.html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ", headers=headers).text
        except:
            if DLG == True:
                self.dialog.close()
            xbmcgui.Dialog().notification("TV.SMS.cz","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)
        if DLG == True:
            self.dialog.close()
        self.ch = {}


    def all_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                try:
                    icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                except:
                    icon = ""
                W.addChannel({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch

    def cz_sk_channels(self):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                if i.find("p").text == "České" or i.find("p").text == "Slovenské":
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    W.addChannel({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch

    def own_channels(self, cchc):
        try:
            root = ET.fromstring(self.html)
            for i in root.iter("a"):
                if i.attrib["id"] in cchc:
                    self.ch[i.attrib["id"]] = encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower())
                    try:
                        icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
                    except:
                        icon = ""
                    W.addChannel({"display-name": [(replace_names(i.find("n").text), u"cs")], "id": encode((i.attrib["id"] + "-" + i.find("n").text).replace(" ", "-").lower()), "icon": [{"src": icon}]})
        except:
            pass
        return self.ch


class Get_programmes_sms:

    def __init__(self, days_back, days):
        self.programmes_sms = []
        self.days_back = days_back
        self.days = days
        self.dialog = xbmcgui.DialogProgressBG()
        if DLG == True:
            self.dialog.create("TV.SMS.cz", "")
            self.dialog.update(0, "TV.SMS.cz","Stahování dat...")

    def data_programmes(self, ch):
        try:
            if ch != {}:
                chl = ",".join(ch.keys())
                now = datetime.now()
                st = 1
                for i in range(self.days_back*-1, self.days):
                    next_day = now + timedelta(days = i)
                    date = next_day.strftime("%Y-%m-%d")
                    date_ = next_day.strftime("%d.%m.%Y")
                    headers = {"user-agent": "SMSTVP/1.7.3 (242;cs_CZ) ID/ef284441-c1cd-4f9e-8e30-f5d8b1ac170c HW/Redmi Note 7 Android/10 (QKQ1.190910.002)"}
                    html = requests.get("http://programandroid.365dni.cz/android/v6-program.php?datum=" + date + "&id_tv=" + chl, headers=headers).text
                    root = ET.fromstring(html)
                    root[:] = sorted(root, key=lambda child: (child.tag,child.get("o")))
                    for i in root.iter("p"):
                        n = i.find("n").text
                        try:
                            k = i.find("k").text
                        except:
                            k = ""
                        if i.attrib["id_tv"] in ch:
                            if ch[i.attrib["id_tv"]] == "1455-nova-+1":
                                TS = TimeShift1
                            else:
                                TS = TimeShift
                            W.addProgramme({"channel": ch[i.attrib["id_tv"]].replace("804-ct-art", "805-ct-:d"), "start": i.attrib["o"].replace("-", "").replace(":", "").replace(" ", "") + TS, "stop": i.attrib["d"].replace("-", "").replace(":", "").replace(" ", "") + TS, "title": [(n, "")], "desc": [(k, "")]})
                    per = int(int(addon.getSetting("num_days_back")) + int(addon.getSetting("num_days")))
                    percent = int((float(st*100) / per))
                    if DLG == True:
                        self.dialog.update(percent, "TV.SMS.cz", date_)
                    st += 1
                if DLG == True:
                    self.dialog.update(100, "TV.SMS.cz", date_)
                    time.sleep(0.5)
                    self.dialog.close()
        except:
            if DLG == True:
                self.dialog.close()
            self.programmes_sms = []
            xbmcgui.Dialog().notification("TV.SMS.cz","Nedostupné", xbmcgui.NOTIFICATION_ERROR, 5000, sound = False)


def generator():
    notice("Generuje se...", 0)
    channels = []
    programmes = []
    cchc = ""
    tm_id = ""
    o2_id = ""
    channels_type = addon.getSetting("category")
    days = int(addon.getSetting("num_days"))
    days_back = int(addon.getSetting("num_days_back"))
    if channels_type == "0":
        if addon.getSetting("sms") == "true":
            g = Get_channels_sms()
            ch = g.all_channels()
            gg = Get_programmes_sms(days_back, days)
            gg.data_programmes(ch)
        if addon.getSetting("t-m") == "true":
            tm_id = ""
            get_tm_programmes(tm_id, days, days_back, "cz")
        if addon.getSetting("mag") == "true":
            mag_id = ""
            get_tm_programmes(mag_id, days, days_back, "sk")
        if addon.getSetting("o2tv") == "true":
            o2_id = "O2 Sport HD,O2 Fotbal HD,O2 Tenis HD,O2 Sport1 HD,O2 Sport2 HD,O2 Sport3 HD,O2 Sport4 HD,O2 Sport5 HD,O2 Sport6 HD,O2 Sport7 HD,O2 Sport8 HD"
            cho2 = {"display-name": [(replace_names("O2TV Sport"), u"cs")], "id": "o2tv-sport", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Fotbal"), u"cs")], "id": "o2tv-fotbal", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-fotbal.png'}]}, {"display-name": [(replace_names("O2TV Tenis"), u"cs")], "id": "o2tv-tenis", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-tenis.png'}]}, {"display-name": [(replace_names("O2TV Sport1"), u"cs")], "id": "o2tv-sport1", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport2"), u"cs")], "id": "o2tv-sport2", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport3"), u"cs")], "id": "o2tv-sport3", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport4"), u"cs")], "id": "o2tv-sport4", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport5"), u"cs")], "id": "o2tv-sport5", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport6"), u"cs")], "id": "o2tv-sport6", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport7"), u"cs")], "id": "o2tv-sport7", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport8"), u"cs")], "id": "o2tv-sport8", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}
            for x in cho2:
                W.addChannel(x)
            get_o2_programmes(o2_id)
        if addon.getSetting("es") == "true":
            es_id = "Eurosport3,Eurosport4,Eurosport5"
            cheu = {"display-name": [(replace_names("Eurosport 3"), u"cs")], "id": "eurosport-3", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/win/eurosport-3.png'}]}, {"display-name": [(replace_names("Eurosport 4"), u"cs")], "id": "eurosport-4", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/win/eurosport-4.png'}]}, {"display-name": [(replace_names("Eurosport 5"), u"cs")], "id": "eurosport-5", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/win/eurosport-5.png'}]}
            for x in cheu:
                W.addChannel(x)
            get_eurosport_programmes(es_id)
        if addon.getSetting("mujtv") == "true":
            get_muj_tv_programmes("723,233,234,110,40,41,49,50,39,37,38,174,52,54,53,393,216,46,408,892,1040", days, days_back)
        if addon.getSetting("stv") == "true":
            get_stv_programmes("", days, days_back)
        if addon.getSetting("stvsk") == "true":
            get_stvsk_programmes("", days, days_back)
        if addon.getSetting("tvspiel") == "true":
            tv_spiel_id = "EURO,EURO2,HDSPO,SHD2,SPO-A,ORFSP"
            get_tv_spiel_programmes(tv_spiel_id, days, days_back)
        if addon.getSetting("ottplay") == "true":
            ott_play_id = "7:2777,7:2779,7:2528,ITbas:SuperTennis.it"
            get_ott_play_programmes(ott_play_id)
    elif channels_type == "1":
        if os.path.exists(custom_channels):
            cchc = open(custom_channels).read()
            if cchc != "":
                g = Get_channels_sms()
                cchc = cchc.split(",")
                ch = g.own_channels(cchc)
                gg = Get_programmes_sms(days_back, days)
                gg.data_programmes(ch)
        if os.path.exists(custom_channels_tm):
            tm_id = open(custom_channels_tm).read()
            if tm_id != "":
                get_tm_programmes(tm_id, days, days_back, "cz")
        if os.path.exists(custom_channels_mag):
            mag_id = open(custom_channels_mag).read()
            if mag_id != "":
                get_tm_programmes(mag_id, days, days_back, "sk")
        if os.path.exists(custom_channels_o2):
            o2_id = open(custom_channels_o2).read()
            if o2_id != "":
                o2_id_list = o2_id.split(",")
                if "O2 Sport HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport"), u"cs")], "id": "o2tv-sport", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Fotbal HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Fotbal"), u"cs")], "id": "o2tv-fotbal", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-fotbal.png'}]})
                if "O2 Tenis HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Tenis"), u"cs")], "id": "o2tv-tenis", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-tenis.png'}]})
                if "O2 Sport1 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport1"), u"cs")], "id": "o2tv-sport1", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport2 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport2"), u"cs")], "id": "o2tv-sport2", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport3 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport3"), u"cs")], "id": "o2tv-sport3", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport4 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport4"), u"cs")], "id": "o2tv-sport4", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport5 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport5"), u"cs")], "id": "o2tv-sport5", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport6 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport6"), u"cs")], "id": "o2tv-sport6", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport7 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport7"), u"cs")], "id": "o2tv-sport7", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                if "O2 Sport8 HD" in o2_id_list:
                    W.addChannel({"display-name": [(replace_names("O2TV Sport8"), u"cs")], "id": "o2tv-sport8", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]})
                get_o2_programmes(o2_id)
        if os.path.exists(custom_channels_mujtv):
            mujtv_id = open(custom_channels_mujtv).read()
            if mujtv_id != "":
                get_muj_tv_programmes(mujtv_id, days, days_back)
        if os.path.exists(custom_channels_es):
            es_id = open(custom_channels_es).read()
            if es_id != "":
                es_id_list = es_id.split(",")
                if "Eurosport3" in es_id_list:
                    W.addChannel({"display-name": [(replace_names("Eurosport 3"), u"cs")], "id": "eurosport-3", "icon": [{"src": 'https://www.o2tv.cz/assets/images/tv-logos/win/eurosport-3.png'}]})
                if "Eurosport4" in es_id_list:
                    W.addChannel({"display-name": [(replace_names("Eurosport 4"), u"cs")], "id": "eurosport-4", "icon": [{"src": 'https://www.o2tv.cz/assets/images/tv-logos/win/eurosport-4.png'}]})
                if "Eurosport5" in es_id_list:
                    W.addChannel({"display-name": [(replace_names("Eurosport 5"), u"cs")], "id": "eurosport-5", "icon": [{"src": 'https://www.o2tv.cz/assets/images/tv-logos/win/eurosport-5.png'}]})
                get_eurosport_programmes(es_id)
        if os.path.exists(custom_channels_stv):
            stv_id = open(custom_channels_stv).read()
            if stv_id != "":
                get_stv_programmes(stv_id, days, days_back)
        if os.path.exists(custom_channels_stvsk):
            stv_id = open(custom_channels_stvsk).read()
            if stv_id != "":
                get_stvsk_programmes(stv_id, days, days_back)
        if os.path.exists(custom_channels_tvspiel):
            tvspiel_id = open(custom_channels_tvspiel).read()
            if tvspiel_id != "":
                get_tv_spiel_programmes(tvspiel_id, days, days_back)
        if os.path.exists(custom_channels_ottplay):
            ottplay_id = open(custom_channels_ottplay).read()
            if ottplay_id != "":
                get_ott_play_programmes(ottplay_id)
    else:
        xbmcgui.Dialog().notification("365 EPG Generator","Žádné kanály", xbmcgui.NOTIFICATION_ERROR, 4000, sound = True)
        return
    if W.get_channels is not None:
        try:
            dialog = xbmcgui.DialogProgressBG()
            if DLG == True:
                dialog.create("365 EPG Generator", "")
                dialog.update(0, "365 EPG Generator", "Generování...")
            W.write(temp_epg, pretty_print=True)
            if DLG == True:
                time.sleep(0.5)
                dialog.update(100, "365 EPG Generator", "Generovaní")
                time.sleep(0.5)
                dialog.update(0, "365 EPG Generator", "Ukládání...")
            xbmcvfs.copy(temp_epg, download_path + addon.getSetting("file_name"))
            xbmcvfs.delete(temp_epg)
            if DLG == True:
                time.sleep(0.5)
                dialog.update(100, "365 EPG Generator", "Hotovo")
                time.sleep(0.5)
                dialog.close()
            notice("Hotovo, uloženo ve složce", 0)
            if sys.argv[0] == "start.py":
                restart_pvr()
        except:
            dialog.close()
            xbmcgui.Dialog().notification("365 EPG Generator","Chyba", xbmcgui.NOTIFICATION_ERROR, 4000, sound = True)
    else:
        xbmcgui.Dialog().notification("365 EPG Generator","Žádné kanály", xbmcgui.NOTIFICATION_ERROR, 4000, sound = True)