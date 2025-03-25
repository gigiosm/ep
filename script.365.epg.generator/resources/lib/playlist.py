# -*- coding: utf-8 -*-

import re
import os
import xbmcgui
import xbmcaddon
import xbmc
import py_m3u8
import unicodedata
import requests
import xml.etree.ElementTree as ET
from py_m3u8 import protocol
from py_m3u8.parser import save_segment_custom_value


addon = xbmcaddon.Addon(id='script.365.epg.generator')
prs = 0


def encode(string):
    if addon.getSetting("diacritics") == "false":
        string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
    return string


def parse_iptv_attributes(line, lineno, data, state):
    if line.startswith(protocol.extinf):
        title = ''
        chunks = line.replace(protocol.extinf + ':', '').rsplit(',', 1)
        if len(chunks) == 2:
            duration_and_props, title = chunks
        elif len(chunks) == 1:
            duration_and_props = chunks[0]

        additional_props = {}
        chunks = duration_and_props.strip().split(' ', 1)
        if len(chunks) == 2:
            duration, raw_props = chunks
            matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
            for match in matched_props:
                additional_props[match.group(1)] = match.group(2)
        else:
            duration = duration_and_props

        if 'segment' not in state:
            state['segment'] = {}
        state['segment']['duration'] = float(duration)
        state['segment']['title'] = title
        save_segment_custom_value(state, 'extinf_props', additional_props)
        state['expect_segment'] = True
        return True


def parse_segments(uri, index, id):
    playlist = '#EXTM3U\n'
    parsed = py_m3u8.load(uri, custom_tags_parser=parse_iptv_attributes)
    for p in parsed.segments:
        parsed.segments[index].custom_parser_values['extinf_props']['tvg-id'] = id
        tags = p.custom_parser_values['extinf_props']
        t = ""
        for x,y in tags.items():
            t = t + x + '="' + y + '" '
        playlist = playlist + '#EXTINF:-1 ' + t[:-1] + ',' + p.title + '\n' + p.uri + '\n'
    return playlist


def parse_names(uri):
    n = []
    parsed = py_m3u8.load(uri, custom_tags_parser=parse_iptv_attributes)
    for p in parsed.segments:
        try:
            id = p.custom_parser_values['extinf_props']["tvg-id"]
        except:
            id = ""
        try:
            logo = p.custom_parser_values['extinf_props']["tvg-logo"]
        except:
            logo = ""
        n.append((p.title, id, logo))
    return n


def get_nonexistant_path(fname_path):
    filename, file_extension = os.path.splitext(fname_path)
    new_fname = "{}-{}{}".format(filename, "new", file_extension)
    return new_fname


def save_playlist(uri, index, id):
    new_playlist = parse_segments(uri, index, id)
    f = open(uri, "w", encoding="utf-8")
    f.write(new_playlist)
    f.close()
    channels(uri, index)


def source7(check):
    ch = [('Penthouse Gold', '7:2777', 'http://pics.cbilling.pw/streams/penthouse1-hd.png'), ('Penthouse Quickies', '7:2779', 'http://pics.cbilling.pw/streams/penthouse2-hd.png'), ('Vivid Red', '7:2528', 'http://pics.cbilling.pw/streams/vivid-red-hd.png'), ('Super Tennis', 'ITbas:SuperTennis.it', 'https://guidatv.sky.it/logo/5246supertennishd_Light_Fit.png?checksum=13f5cbb1646d848fde3af6fccba8dd4c')]
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select("OTT Play", [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source6(check):
    ch = [('Eurosport 1 (DE)', 'EURO', 'http://live.tvspielfilm.de/static/images/channels/large/EURO.png'), ('Eurosport 2 (DE)', 'EURO2', 'http://live.tvspielfilm.de/static/images/channels/large/EURO2.png'), ('Sky Sport 1 (DE)', 'HDSPO', 'http://live.tvspielfilm.de/static/images/channels/large/HDSPO.png'), ('Sky Sport 2 (DE)', 'SHD2', 'http://live.tvspielfilm.de/static/images/channels/large/SHD2.png'), ('Sky Sport Austria1', 'SPO-A', 'http://live.tvspielfilm.de/static/images/channels/large/SPO-A.png'), ('ORF Sport+', 'ORFSP', 'http://live.tvspielfilm.de/static/images/channels/large/ORFSP.png')]
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select("TV Spiel", [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source5(check):
    ch = [('Eurosport 3', 'eurosport-3', 'http://www.o2tv.cz/assets/images/tv-logos/win/eurosport-3.png'), ('Eurosport 4', 'eurosport-4', 'http://www.o2tv.cz/assets/images/tv-logos/win/eurosport-4.png'), ('Eurosport 5', 'eurosport-5', 'http://www.o2tv.cz/assets/images/tv-logos/win/eurosport-5.png')]
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select("Eurosport", [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source4(check):
    ch = [('Skylink 7', '723-skylink-7', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ac6c69625699eaecc9b39f7ea4d69b8c&amp;p2=80'), ('Stingray Classica', '233-stingray-classica', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=661af53f8f3b997611c29f844c7006fd&amp;p2=80'), ('Stingray iConcerts', '234-stingray-iconcerts', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=99c87946872c81f46190c77af7cd1d89&amp;p2=80'), ('Stingray CMusic', '110-stingray-cmusic', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=b323f2ad3200cb938b43bed58dd8fbf9&amp;p2=80'), ('ORF1', '40-orf1', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=422162d3082a84fc97a7fb9b3ad6823f&amp;p2=80'), ('ORF2', '41-orf2', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=477dcc38e54309f5db7aec56b62b4cdf&amp;p2=80'), ('RTL', '49-rtl', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=7cb9005e66956c56fd0671ee79ee2471&amp;p2=80'), ('RTL2', '50-rtl2', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=418e0d04529ea3aaa2bc2c925ddf5982&amp;p2=80'), ('Polsat', '39-polsat', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=f54e290782e8352303cfe43ce949d339&amp;p2=80'), ('TVP1', '37-tvp1', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=770431539d1fa662f705c1c05a0dd943&amp;p2=80'), ('TVP2', '38-tvp2', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e2ce4065f27ce199f7613f38878cef72&amp;p2=80'), ('Pro7', '174-pro7', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e23a7fb8caff9ff514f254c43a39d9b6&amp;p2=80'), ('SAT1', '52-sat1', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=97dd916e0164fff141065c3fba71c291&amp;p2=80'), ('Kabel1', '54-kabel1', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=be6dc88dd3c1c243ba4f28cccb8f1d34&amp;p2=80'), ('VOX', '53-vox', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=d2c68d2b145a5f2e20e5c05c20a9679e&amp;p2=80'), ('ZDF', '393-zdf', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=dad48d516fbdb30321564701cc3faa04&amp;p2=80'), ('ZDF Neo', '216-zdf-neo', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=cd5b8935893b0e4cde41bc3720435f14&amp;p2=80'), ('3SAT', '46-3sat', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=58d350c6065d9355a52c6dbc3b31b185&amp;p2=80'), ('SAT.1 GOLD', '408-sat1-gold', ''), ('Vixen', '892-vixen', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=4499ebafb26a915859febcb4306703ca&amp;p2=80'), ('Canal+ Sport', '1040-canal+sport', 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ab73879fdf9b10e1deb0224bfbb3cfd8&amp;p2=80')]
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select("můjTVprogram.cz", [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source3(check):
    ch = [('O2 Sport', 'o2tv-sport', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Fotbal', 'o2tv-fotbal', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-tv-fotbal.png'), ('O2 Tenis', 'o2tv-tenis', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-tv-tenis.png'), ('O2 Sport1', 'o2tv-sport1', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport2', 'o2tv-sport2', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport3', 'o2tv-sport3', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport4', 'o2tv-sport4', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport5', 'o2tv-sport5', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport6', 'o2tv-sport6', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport7', 'o2tv-sport7', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'), ('O2 Sport8', 'o2tv-sport8', 'http://www.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png')]
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select("O2 TV Sport", [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source2(check, lng):
    if lng == "cz":
        ch = []
        req = requests.get("http://felixtv.wz.cz/epg/channels.php").json()
        for x in req["channels"]:
            ch.append((x["name"], "stv-" + x["id"], "https://sledovanitv.cz/cache/biglogos/" + x["id"] + ".png"))
        title = 'SledovaniTV.cz'
    else:
        ch = []
        req = requests.get("http://felixtv.wz.cz/epg/channels_sk.php").json()
        for x in req["channels"]:
            ch.append((x["name"], "stvsk-" + x["id"], "https://sledovanietv.sk/cache/biglogos/" + x["id"] + ".png"))
        title = 'SledovanieTV.sk'
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select(title, [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source1(check, lng):
    if lng == "cz":
        prfx = "tm-"
        title = 'T-Mobile TV GO'
    else:
        prfx = "mag-"
        title = 'Magio GO'
    ch = []
    params={"dsid": "c75536831e9bdc93", "deviceName": "Xiaomi Mi 11", "deviceType": "OTT_STB", "osVersion": "10", "appVersion": "3.7.0", "language": "CZ"}
    headers={"Host": lng + "go.magio.tv", "authorization": "Bearer", "User-Agent": "okhttp/3.12.12", "content-type":  "application/json", "Connection": "Keep-Alive"}
    req = requests.post("https://" + lng + "go.magio.tv/v2/auth/init", params=params, headers=headers, verify=True).json()
    token = req["token"]["accessToken"]
    headers2={"Host": lng + "go.magio.tv", "authorization": "Bearer " + token, "User-Agent": "okhttp/3.12.12", "content-type":  "application/json"}
    req1 = requests.get("https://" + lng + "go.magio.tv/v2/television/channels?list=LIVE&queryScope=LIVE", headers=headers2).json()["items"]
    for y in req1:
        id = str(y["channel"]["channelId"])
        name = y["channel"]["name"]
        ch.append((name.replace(" HD", ""), prfx + id + "-" + encode(name).replace(" HD", "").lower().replace(" ", "-")))
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select(title, [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def source0(check):
    ch = []
    html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ").text
    root = ET.fromstring(html)
    for i in root.iter('a'):
        try:
            icon = "http://sms.cz/kategorie/televize/bmp/loga/velka/" + i.find("o").text
        except:
            icon = ""
        ch.append((i.find('n').text, encode((i.attrib["id"] + "-" + i.find('n').text).replace(" ", "-").lower()), icon))
    chch = [idx for idx in ch if idx[0][0].lower() == check.lower()]
    ch.sort()
    for c in ch:
        if c not in chch:
            chch.append(c)
    channel = xbmcgui.Dialog().select('TV.SMS.cz', [x[0] for x in chch], useDetails=False)
    if channel != -1:
        return chch[channel][1]
    else:
        return None


def sources(uri, channel, check):
    source = xbmcgui.Dialog().select('Zdroj', ["TV.SMS.cz", "T-Mobile TV GO", "Magio GO", "SledovaniTV.cz", "SledovanieTV.sk", "O2 TV Sport", "můjTVprogram.cz", "Eurosport", "TV Spiel", "OTT Play"], useDetails=False)
    if source != -1:
        if source == 0:
            id = source0(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 1:
            id = source1(check, "cz")
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 2:
            id = source1(check, "sk")
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 3:
            id = source2(check, "cz")
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 4:
            id = source2(check, "sk")
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 5:
            id = source3(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 6:
            id = source4(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 7:
            id = source5(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 8:
            id = source6(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
        elif source == 9:
            id = source7(check)
            if id is not None:
                save_playlist(uri, channel, id)
            else:
                channels(uri, channel)
    else:
        channels(uri, channel)


def channels(uri, prs):
    name_list = parse_names(uri)
    item = []
    for x in name_list:
        inner_item = xbmcgui.ListItem(label="[COLOR lightskyblue]" + x[0] + "[/COLOR]", label2=x[1])
        inner_item.setArt({ 'thumb': x[2]})
        item.append(inner_item)
    channel = xbmcgui.Dialog().select('Playlist', item, useDetails=True, preselect = prs)
    if channel != -1:
        sources(uri, channel, name_list[channel][0][0])



uri = xbmcgui.Dialog().browse(1,"Vyberte m3u soubor","files", ".m3u|.txt", defaultt = addon.getSetting("pls_path"))
if uri:
#    fname = get_nonexistant_path(uri)
    addon.setSetting(id='pls_path', value= uri)
    channels(uri, prs)