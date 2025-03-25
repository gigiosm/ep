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
custom_names = xbmcvfs.translatePath("%s/custom_names.txt" % userpath)
if not xbmcvfs.exists(userpath):
    xbmcvfs.mkdir(userpath)


def query(ch, i):
    kb = xbmc.Keyboard("", "Zadejte název kanálu")
    kb.doModal()
    if not kb.isConfirmed():
        return
    q = kb.getText()
    if "=" not in ch[i]:
        ch[i] = ch[i] + "=" + q
    else:
        c = ch[i].split("=")[0]
        ch[i] = c + "=" + q
    if ch[i][-1] == "=":
        ch[i] = ch[i][:-1].replace("[COLOR lightskyblue]", "").replace("[/COLOR]", "")
    select(ch, i)


def select(channels, ps):
    for c in channels:
        if "=" in c:
            channels[channels.index(c)] = "[COLOR lightskyblue]" + c + "[/COLOR]"
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    dialog = xbmcgui.Dialog()
    index = dialog.select("Upravit", channels, preselect = ps)
    if index == -1:
        f = open(custom_names, "w", encoding="utf-8")
        for x in channels:
            if "=" in x:
                f.write(x.replace("[COLOR lightskyblue]", "").replace("[/COLOR]", "") + "\n")
        f.close()
        xbmcgui.Dialog().notification("365 EPG Generator","Uloženo", xbmcgui.NOTIFICATION_INFO, 1000, sound = False)
    else:
        query(channels, index)


def run():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    channels = ["BBC Earth", "Digi Sport 6", "Digi Sport 7", "Digi Sport 8", "Digi Sport 9", "Skylink 7", "Stingray Classica", "Stingray iConcerts", "Stingray CMusic"]
    html = requests.get("http://programandroid.365dni.cz/android/v6-tv.php?locale=cs_CZ").text
    root = ET.fromstring(html)
    for i in root.iter('a'):
        channels.append(i.find('n').text)
    if os.path.exists(custom_names):
        try:
            ch = open(custom_names, "r",encoding="utf-8").read().split("\n")
            for x in channels:
                for y in ch:
                    if y.split("=")[0] == x:
                        channels[channels.index(x)] = y
        except:
            pass
    select(channels, -1)


if __name__ == "__main__":
    run()