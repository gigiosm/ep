# -*- coding: utf-8 -*-

import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui

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
channels_select_path = xbmcvfs.translatePath("%s/channels.json" % userpath)

try:
    xbmcvfs.delete(custom_channels)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_tm)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_o2)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_mujtv)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_es)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_stv)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_stvsk)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_mag)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_tvspiel)
except:
    pass
try:
    xbmcvfs.delete(custom_channels_ottplay)
except:
    pass
try:
    xbmcvfs.delete(channels_select_path)
except:
    pass
xbmcgui.Dialog().notification("365 EPG Generator","Obnoveno", xbmcgui.NOTIFICATION_INFO, 1000, sound = False)
