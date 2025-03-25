# -*- coding: utf-8 -*-

import xbmcaddon
import sys
import xbmc
import xbmcgui
from resources.lib import schedule


addon = xbmcaddon.Addon(id='script.365.epg.generator')
interval = {'0': 1, '1': 3, '2': 6}
interval2 = {'0': ' - Interval: 1 den', '1': ' - Interval: 3 dny', '2': ' - Interval: 6 dní'}
monitor = xbmc.Monitor()


def start():
    xbmc.executebuiltin('RunAddon("script.365.epg.generator")')


job = schedule.every(interval[addon.getSetting("interval")]).days.at(addon.getSetting("auto_time")).do(start)


def update():
    if addon.getSetting("start_enabled") == "true":
        xbmc.executebuiltin('RunScript("special://home/addons/script.365.epg.generator/resources/lib/start.py")')
    if addon.getSetting("auto_enabled") == "true":
        if addon.getSetting("notice") == "true":
            xbmcgui.Dialog().notification("365 EPG Generator","Čas: " + addon.getSetting("auto_time") + interval2[addon.getSetting("interval")], xbmcgui.NOTIFICATION_INFO, 4000, sound = False)
        while not monitor.abortRequested():
            if monitor.waitForAbort(1):
                schedule.cancel_job(job)
                break

            if addon.getSetting("auto_enabled") == "false":
                schedule.cancel_job(job)
                break
            schedule.run_pending()
    if addon.getSetting("notice") == "true":
        xbmcgui.Dialog().notification("365 EPG Generator","Vypnutá automatická aktualizace", xbmcgui.NOTIFICATION_INFO, 4000, sound = False)
    sys.exit(0)


if __name__ == '__main__':
    update()