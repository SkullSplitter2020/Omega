import os, xbmcgui, xbmc, xbmcvfs, glob, shutil

def run():
    if os.path.exists(xbmcvfs.translatePath('special://home/addons/skin.TechNEWSology')):
        xbmc.sleep(5000)
        xbmcgui.Dialog().notification('[B][COLOR orange]TechNEWSology Repository - Πατάμε Ναι[/COLOR][/B]', '[B][COLOR white]μετά το πάγωμα της εικόνας, αν δεν εγκατασταθεί μόνο του το repository[/COLOR][/B]', 'special://skin/icon.png', sound=False)
        xbmc.sleep(5000)
        base_path = xbmcvfs.translatePath('special://home/addons')
        dir_list = glob.iglob(os.path.join(base_path, "repository.TechNEWSology"))
        for path in dir_list:
            if os.path.isdir(path):
                shutil.rmtree(path)
                xbmc.sleep(2000)
                xbmc.executebuiltin("LoadProfile(Master user)")
                xbmc.sleep(15000)
                xbmc.executebuiltin('InstallAddon(repository.TechNEWSology)')
                if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
                    xbmc.sleep(1200)
                    xbmc.executebuiltin('SendClick(11)')
                    xbmc.sleep(1200)
                    xbmc.executebuiltin('SendClick(11)')
                    xbmc.sleep(1000)
                    xbmc.executebuiltin('SendClick(11)')
                    xbmc.sleep(20000)
                    xbmcvfs.delete('special://home/addons/repository.Worldrepo/service.py')
        xbmc.sleep(5000)
        xbmc.executebuiltin('InstallAddon(repository.TechNEWSology)')
        if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
            xbmc.sleep(1200)
            xbmc.executebuiltin('SendClick(11)')
            xbmc.sleep(1200)
            xbmc.executebuiltin('SendClick(11)')
            xbmc.sleep(20000)
            xbmcvfs.delete('special://home/addons/repository.Worldrepo/service.py')

run()
