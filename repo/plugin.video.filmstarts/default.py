# -*- coding: utf-8 -*-

'''
    Copyright (C) 2024 realvito

    FILMSTARTS.de

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from resources.lib.common import *
from resources.lib import navigator


def run():
	if mode == 'root': ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False    ##### [plugin.video.filmstarts v.1.1.0+v.1.1.2] - 31.12.2023 + 28.02.2024 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join('special://home{0}addons{0}{1}{0}lib{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
		UNO = os.path.join(firstSCRIPT, 'only_at_FIRSTSTART')
		if xbmcvfs.exists(UNO):
			sourceUSER = xbmcvfs.translatePath(os.path.join('special://home{0}userdata{0}addon_data{0}{1}{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(sourceUSER):
				try:
					xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":false}}}}'.format(addon_id))
					shutil.rmtree(sourceUSER, ignore_errors=True)
				except: pass
				xbmcvfs.delete(UNO)
				xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":true}}}}'.format(addon_id))
				xbmc.sleep(500)
				DONE = True
			else:
				xbmcvfs.delete(UNO)
				xbmc.sleep(500)
				DONE = True
		else:
			DONE = True
		if DONE is True: navigator.mainMenu()
	elif mode == 'trailers':
		navigator.trailers(target)
	elif mode == 'movies':
		navigator.movies()
	elif mode == 'series':
		navigator.series()
	elif mode == 'filtrating':
		navigator.filtrating(url, target)
	elif mode == 'selectionArticles':
		navigator.selectionArticles(url, target, extras)
	elif mode == 'selectionWeeks':
		navigator.selectionWeeks(url)
	elif mode == 'listVideos':
		navigator.listVideos(url, page, position, target)
	elif mode == 'playCODE':
		navigator.playCODE(IDENTiTY)
	elif mode == 'callingMain':
		navigator.mainMenu()
		xbmc.executebuiltin(f"Container.Update({HOST_AND_PATH}, replace)")
		return sys.exit(0)
	elif mode == 'blankFUNC':
		pass # do nothing
	elif mode == 'aConfigs':
		addon.openSettings()

run()
