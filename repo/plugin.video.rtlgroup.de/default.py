# -*- coding: utf-8 -*-

'''
    Copyright (C) 2024 realvito

    RTLPLUS - NW

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
from resources.lib import mediatools
from resources.lib import navigator
import inputstreamhelper


def run():
	if mode in ['root', 'playDash']: ##### Delete old ACCOUNT-TOKENS in Userdata-Folder #####
		DONE = False    ##### [plugin.video.rtlgroup.de v.1.1.1+v.1.1.2+v.1.1.7] - 18.02.2023+24.02.2023+19.11.2023 #####
		firstSCRIPT = xbmcvfs.translatePath(os.path.join('special://home{0}addons{0}{1}{0}lib{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
		UNO = xbmcvfs.translatePath(os.path.join(firstSCRIPT, 'only_at_FIRSTSTART'))
		if xbmcvfs.exists(UNO):
			OLD_SESS = xbmcvfs.translatePath(os.path.join('special://home{0}userdata{0}addon_data{0}{1}{0}tempSESS{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
			OLD_FREE = xbmcvfs.translatePath(os.path.join('special://home{0}userdata{0}addon_data{0}{1}{0}tempFREE{0}'.format(os.sep, addon_id))).encode('utf-8').decode('utf-8')
			try:
				xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":false}}}}'.format(addon_id))
				if xbmcvfs.exists(OLD_SESS):
					shutil.rmtree(OLD_SESS, ignore_errors=True) # Delete oldSESS-Folder
				if xbmcvfs.exists(OLD_FREE):
					shutil.rmtree(OLD_FREE, ignore_errors=True) # Delete oldFREE-Folder
			except: pass
			xbmcvfs.delete(UNO)
			xbmc.executeJSONRPC('{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{}", "enabled":true}}}}'.format(addon_id))
			xbmc.sleep(500)
			DONE = True
		else:
			DONE = True
		if DONE is True:
			if mode == 'root':
				if addon.getSetting('checkwidevine') == 'true':
					debug_MS("(default.checkwidevine) ### Die regelmässige Widevineüberprüfung ist für dieses Addon aktiviert !!! ###")
					is_helper = inputstreamhelper.Helper('mpd', drm='com.widevine.alpha')
					if is_helper.check_inputstream():
						debug_MS("(default.checkwidevine) ### Widevine ist auf diesem Gerät installiert und aktuell !!! ###")
					else:
						failing("(default.checkwidevine) ERROR - ERROR - ERROR :\nXXXXX !!! Widevine oder Inputstream.Adaptive wurde auf diesem Gerät NICHT gefunden !!! XXXXX")
						dialog.notification(translation(30521).format('Widevine', ''), translation(30561), icon, 12000)
				navigator.mainMenu()
			elif mode == 'playDash':
				navigator.playDash(action, xcode, xlink, xdrm, xfree, xtele)
	elif mode == 'create_account':
		navigator.create_account()
	elif mode == 'erase_account':
		navigator.erase_account()
	elif mode == 'listSeries':
		navigator.listSeries(url, extras, searching)
	elif mode == 'listSeasons':
		navigator.listSeasons(url, photo)
	elif mode == 'listEpisodes':
		navigator.listEpisodes(url, extras, xcode)
	elif mode == 'listStations':
		navigator.listStations()
	elif mode == 'listAlphabet':
		navigator.listAlphabet()
	elif mode == 'listNewest':
		navigator.listNewest()
	elif mode == 'listDates':
		navigator.listDates()
	elif mode == 'listTopics':
		navigator.listTopics()
	elif mode == 'listGenres':
		navigator.listGenres()
	elif mode == 'listThemes':
		navigator.listThemes()
	elif mode == 'SearchRTLPLUS':
		navigator.SearchRTLPLUS()
	elif mode == 'listLivestreams':
		navigator.listLivestreams()
	elif mode == 'listFavorites':
		navigator.listFavorites()
	elif mode == 'favs':
		navigator.favs(action, name, pict, url, plot, type)
	elif mode == 'blankFUNC':
		pass # do nothing
	elif mode == 'preparefiles':
		mediatools.preparefiles(url, name, extras, cycle)
	elif mode == 'generatefiles':
		mediatools.generatefiles(url, name)
	elif mode == 'clear_storage':
		navigator.clear_storage()
	elif mode == 'aConfigs':
		addon.openSettings()
	elif mode == 'iConfigs':
		xbmcaddon.Addon('inputstream.adaptive').openSettings()

run()
