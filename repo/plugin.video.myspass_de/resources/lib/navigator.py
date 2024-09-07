# -*- coding: utf-8 -*-

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	addDir(translation(30601), artpic+'favourites.png', {'mode': 'listShowsFavs'})
	addDir(translation(30602), icon, {'mode': 'listEpisodes', 'url': BASE_LONG})
	addDir(translation(30603), icon, {'mode': 'listSelections', 'url': 'CHANNELS'})
	addDir(translation(30604), icon, {'mode': 'listSelections', 'url': 'TV SHOWS'})
	addDir(translation(30605), icon, {'mode': 'listSelections', 'url': 'WEB SHOWS'})
	addDir(translation(30606), icon, {'mode': 'listSelections', 'url': 'STAND UP'})
	addDir(translation(30607), icon, {'mode': 'listSelections', 'url': 'SERIEN'})
	addDir(translation(30608), icon, {'mode': 'listAlphabet'})
	addDir(translation(30609), icon, {'mode': 'listShows', 'url': 'standard'})
	if enableADJUSTMENT:
		addDir(translation(30610), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'Z', '??']:
		addDir(letter, alppic+letter.replace('??', 'QM')+'.jpg', {'mode': 'listShows', 'url': letter.replace('0-9', '1').replace('??', 'QM')})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listShows(TYPE):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listShows) -------------------------------------------------- START = listShows --------------------------------------------------")
	debug_MS(f"(navigator.listShows) ### URL or LETTER : {TYPE} ###")
	content = getUrl(f'{BASE_URL}/sendungen-a-bis-z/')
	if TYPE == 'QM':
		result = re.compile(r'<h3 class="category__headline">(.*?)</div>          </div>\s*</div>', re.S).findall(content)[-1]
	elif len(TYPE) < 4:
		result = re.findall(f'<div class="category clearfix" id="{TYPE}">(.*?)(?:<div class="category clearfix"|<footer class=)', content, re.S)[0]
	else:
		result = re.findall(r'<div id="content" class="container">(.*?)<footer class=', content, re.S)[0]
	spl = result.split('<div class="category__item">')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		title = re.compile(r' alt=["\']([^"]+?)["\']/>', re.S).findall(entry)[0]
		title = cleaning(title)
		link = re.compile(r'<a href=["\']([^"]+?)["\']', re.S).findall(entry)[0]
		link = BASE_URL+link if link[:4] != 'http' else link
		link = link.replace('UNKNOWN', 'tvshows').replace('das-rtl-turmspringen', 'rtl-turmspringen').replace('besten-comedians', 'besten-comediens')
		photo = re.compile(r'(?:img["\'] src=|data-src=)["\']([^"]+?)["\']', re.S).findall(entry)[0].replace('-300x169.', '.')
		photo = cleanPhoto(photo)
		debug_MS(f"(navigator.listShows) ##### TITLE = {title} || LINK = {link} || IMAGE = {photo} #####")
		addType = 1
		if xbmcvfs.exists(channelFavsFile):
			with open(channelFavsFile, 'r') as fp:
				watch = json.load(fp)
				for item in watch.get('items', []):
					if item.get('url') == link: addType = 2
		addDir(title, photo, {'mode': 'listSeasons', 'url': link, 'extras': photo, 'origSERIE': title}, addType=addType)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSelections(TYPE):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listSelections) -------------------------------------------------- START = listSelections --------------------------------------------------")
	debug_MS(f"(navigator.listSelections) ### THEMA : {TYPE} ###")
	content = getUrl(f'{BASE_URL}/ganze-folgen/')
	result = re.findall(f'<h3 class="headline has-arrow">{TYPE}</h3>(.*?)(?:<h3 class="headline has-arrow">|<footer class=)', content, re.S)[0]
	spl = result.split('<div class="bacs-item bacs-item--hover')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		title = re.compile(r'(?:<meta itemprop=["\']name["\'] content=| alt=)["\']([^"]+?)["\'](?:/>|>)', re.S).findall(entry)[0]
		title = cleaning(title)
		link = re.compile(r'<a href=["\']([^"]+?)["\']', re.S).findall(entry)[0]
		link = BASE_URL+link if link[:4] != 'http' else link
		link = link.replace('UNKNOWN', 'tvshows').replace('das-rtl-turmspringen', 'rtl-turmspringen').replace('besten-comedians', 'besten-comediens')
		photo = re.compile(r'(?:<meta itemprop=["\']image["\'] content=|data-src=)["\']([^"]+?)["\']', re.S).findall(entry)[0].replace('-300x169.', '.')
		photo = cleanPhoto(photo)
		desc = re.compile(r'<meta itemprop=["\']description["\'] content=["\']([^"]+?)["\']', re.S).findall(entry)
		plot = cleaning(desc[0]) if desc else None
		debug_MS(f"(navigator.listSelections) ##### TITLE = {title} || LINK = {link} || IMAGE = {photo} #####")
		if not 'trailer' in link.lower():
			if TYPE == 'CHANNELS':
				addDir(title, photo, {'mode': 'listEpisodes', 'url': link, 'extras': 'compilation', 'origSERIE': title}, plot)
			else:
				addType = 1
				if xbmcvfs.exists(channelFavsFile):
					with open(channelFavsFile, 'r') as fp:
						watch = json.load(fp)
						for item in watch.get('items', []):
							if item.get('url') == link: addType = 2
				addDir(title, photo, {'mode': 'listSeasons', 'url': link, 'extras': photo, 'origSERIE': title}, plot, addType)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(url, IMG, SERIE):
	debug_MS("(navigator.listSeasons) -------------------------------------------------- START = listSeasons --------------------------------------------------")
	debug_MS(f"(navigator.listSeasons) ### URL : {url} ###")
	COMBI_SEASON = []
	FOUND = 0
	content = getUrl(url)
	SELECTOR = re.search('<select title="Staffel auswählen" class=(.*?)</select>', content, re.S)
	if SELECTOR:
		SEASONS = re.findall(r'<option data-remote-args="(.*?)".+?data-remote-target=.+?>(.*?)</option>', SELECTOR.group(1), re.S)
		for url2, title in SEASONS:
			FOUND += 1
			LINK = f'{BASE_URL}/frontend/php/ajax.php?query=bob&videosOnly=true{url2}'
			title = cleaning(title)
			number = re.compile('([0-9]+)', re.S).findall(title)
			if number:
				title = translation(30620).format(str(number[0])) if 'staffel' in title.lower() else translation(30621) if str(number[0]) == '1' else title.split(' -')[0]
			debug_MS(f"(navigator.listSeasons) ##### TITLE = {title} || LINK = {LINK} #####")
			COMBI_SEASON.append([title, IMG, LINK, SERIE])
	if COMBI_SEASON and FOUND == 1:
		debug_MS("(navigator.listSeasons) ----- Only one Season FOUND - goto = listEpisodes -----")
		for title, IMG, LINK, SERIE in COMBI_SEASON:
			return listEpisodes(LINK, SERIE)
	elif COMBI_SEASON and FOUND > 1:
		for title, IMG, LINK, SERIE in COMBI_SEASON:
			addDir(title, IMG, {'mode': 'listEpisodes', 'url': LINK, 'origSERIE': SERIE})
	else:
		debug_MS("(navigator.listSeasons) ##### Keine SEASON-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30524), translation(30525).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(url, SERIE):
	debug_MS("(navigator.listEpisodes) -------------------------------------------------- START = listEpisodes --------------------------------------------------")
	debug_MS(f"(navigator.listEpisodes) ### URL : {url} ### SERIE : {SERIE} ###")
	SEND = {}
	COMBI_EPISODE, SEND['videos'] = ([] for _ in range(2))
	START_URL, position = url, 0
	content = getUrl(url).replace('\\', '')
	if START_URL == BASE_LONG:
		result = re.findall(r'<div id="content" class="container">(.*?)</article>  </section>', content, re.S)[0]
		spl = result.split('<div class="homeTeaser-overlay Desktop_HomeTeaser')
	elif 'channels/' in START_URL:
		result = re.findall(r'<ul id="playlist_ul">(.*?)</ul>', content, re.S)[0]
		spl = result.split('_video_li">')
	else:
		spl = content.split('bacs-item--hover bacs-item--lg has-infos-shown bacs-item--monthly')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		debug_MS(f"(navigator.listEpisodes) no.01 ##### ENTRY = {str(entry)} #####")
		newSHOW, newTITLE, vidURL, Note_1, Note_2, DESC = ("" for _ in range(6))
		SEAS, EPIS, vidURL_2, vidURL_3, photo, bcDATE, bcDATE_2, bcDATE_3, year, begins = (None for _ in range(10))
		duration, duration_2, duration_3 = ('0' for _ in range(3))
		if START_URL == BASE_LONG:
			title = re.compile(r'<h2 class=["\']title ellipsis["\']>([^<]+?)</h2>', re.S).findall(entry)[0]
		elif 'channels/' in START_URL:
			title = re.compile(r'aria-hidden=["\']true["\']></i>([^<]+?)</a></li>', re.S).findall(entry)[0]
			if 'channel erneut von vorne' in title.lower(): continue
		else:
			title_1 = re.compile(r'class="title" title="(.*?)">', re.S).findall(entry)
			title_2 = re.compile(r' alt="(.*?)"/>', re.S).findall(entry)
			title = title_1[0] if title_1 else title_2[0]
		title = cleaning(title)
		if not 'channels/' in START_URL and ('Teil 2' in title or 'Teil 3' in title): continue
		link = re.compile(r'<a href=["\']([^"]+?)["\']', re.S).findall(entry)[0]
		link = BASE_URL+link if link[:4] != 'http' else link
		try: episID = re.compile(r'https?://(?:www\.)?myspass\.de/([^/]+/)*(?P<id>\d+)', re.S).findall(link)[0][1]
		except: continue
		newSHOW, newTITLE, SEAS, EPIS, DESC, duration, photo, bcDATE, begins, vidURL = getVideodata(episID)
		if vidURL == "": continue
		if not 'channels/' in START_URL and ('Teil 1' in title or 'Teil 1' in newTITLE):
			try:
				shortURL = link.split('www.myspass.de')[1].split('-Teil-')[0] if 'www.myspass.de' in link and '-Teil-' in link else link
				plus_CONTENT = content[content.find('<table class="listView--table">')+1:]
				plus_CONTENT = plus_CONTENT[:plus_CONTENT.find('</table>')]
				match = re.findall(r'<tr data-month(.+?)</tr>', plus_CONTENT, re.S)
				for chtml in match:
					debug_MS("(navigator.listEpisodes) no.02 ##### more Videos CHTML = {} #####".format(str(chtml)))
					url2 = re.compile(r'<a href=["\']([^"]+?)["\']', re.S).findall(chtml)[0]
					fullURL = BASE_URL+url2 if url2[:4] != 'http' else url2
					identical = similar(url2, shortURL)
					if identical is True and 'Teil-2' in fullURL:
						newIDD_2 = re.compile(r'https?://(?:www\.)?myspass\.de/([^/]+/)*(?P<id>\d+)', re.S).findall(fullURL)[0][1]
						newSHOW_2, newTITLE_2, SEAS_2, EPIS_2, DESC_2, duration_2, photo_2, bcDATE_2, begins_2, vidURL_2 = getVideodata(newIDD_2)
						vidURL_2 = '@@'+vidURL_2
					if identical is True and 'Teil-3' in fullURL:
						newIDD_3 = re.compile(r'https?://(?:www\.)?myspass\.de/([^/]+/)*(?P<id>\d+)', re.S).findall(fullURL)[0][1]
						newSHOW_3, newTITLE_3, SEAS_3, EPIS_3, DESC_3, duration_3, photo_3, bcDATE_3, begins_2, vidURL_3 = getVideodata(newIDD_3)
						vidURL_3 = '@@'+vidURL_3
			except: pass
		position += 1
		if vidURL_2: vidURL = vidURL+vidURL_2
		if vidURL_3: vidURL = vidURL+vidURL_3
		duration = int(duration)+int(duration_2)+int(duration_3)
		image = cleanPhoto(photo) if photo else icon
		SERIE = newSHOW if START_URL == BASE_LONG else SERIE
		Note_1 = translation(30622).format(SERIE)
		title = SERIE+' - '+newTITLE if START_URL == BASE_LONG else title.split('- Teil')[0].split(' Teil')[0]
		newTITLE = newTITLE.split(' - Teil')[0].split(' Teil')[0] if 'Teil' in newTITLE else newTITLE
		if str(SEAS).isdigit() and str(EPIS).isdigit() and str(EPIS) != '0':
			SEAS, EPIS = SEAS.zfill(2), EPIS.zfill(2)
			name = translation(30623).format(SEAS, EPIS, title)
			if bcDATE and not '1970' in bcDATE:
				year, Note_2 = str(bcDATE)[10:14], translation(30624).format(SEAS, EPIS, str(bcDATE))
			else: Note_2 = translation(30625).format(SEAS, EPIS)
		else:
			name = title+'  (Special)' if 'spezial' in str(EPIS).lower() else title
			if bcDATE and not '1970' in bcDATE:
				year, Note_2 = str(bcDATE)[10:14], translation(30626).format(newTITLE, str(bcDATE))
			else: Note_2 = '[CR]'
		if 'channels/' in START_URL:
			name = translation(30627).format(str(position).zfill(2), newTITLE)
		uvz = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playCODE', 'IDENTiTY': episID}))
		plot = Note_1+Note_2+DESC.replace('\n', '[CR]')
		debug_MS(f"(navigator.listEpisodes[2]) no.02 ##### NAME : {name} || IDD : {episID} #####")
		debug_MS(f"(navigator.listEpisodes[2]) no.02 ##### SERIE : {SERIE} || BEGINS : {str(begins)} || YEAR : {str(year)} || DURATION : {str(duration)} #####")
		debug_MS(f"(navigator.listEpisodes[2]) no.02 ##### THUMB : {image} || SEASON : {str(SEAS)} || EPISODE : {str(EPIS)} #####")
		COMBI_EPISODE.append([uvz, episID, vidURL, image, name, SERIE, SEAS, EPIS, plot, duration, year, begins])
	if COMBI_EPISODE:
		for uvz, episID, vidURL, image, name, SERIE, SEAS, EPIS, plot, duration, year, begins in COMBI_EPISODE:
			for method in getSorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			LSM = xbmcgui.ListItem(name)
			if plot in ['', 'None', None]: plot = "..."
			cineType = 'episode' if str(EPIS).isdigit() and str(EPIS) != '0' else 'movie'
			playType = 'multi' if '@@' in vidURL else 'single'
			if KODI_ov20:
				vinfo = LSM.getVideoInfoTag()
				if str(SEAS).isdigit(): vinfo.setSeason(int(SEAS))
				if str(EPIS).isdigit(): vinfo.setEpisode(int(EPIS))
				vinfo.setTvShowTitle(SERIE)
				vinfo.setTitle(name)
				vinfo.setPlot(plot)
				if str(duration).isdigit(): vinfo.setDuration(int(duration))
				if begins: LSM.setDateTime(begins)
				if str(year).isdigit(): vinfo.setYear(int(year))
				vinfo.setGenres(['Unterhaltung'])
				vinfo.setStudios(['myspass.de'])
				vinfo.setMediaType(cineType)
			else:
				vinfo = {}
				if str(SEAS).isdigit(): vinfo['Season'] = SEAS
				if str(EPIS).isdigit(): vinfo['Episode'] = EPIS
				vinfo['Tvshowtitle'] = SERIE
				vinfo['Title'] = name
				vinfo['Plot'] = plot
				if str(duration).isdigit(): vinfo['Duration'] = duration
				if begins: vinfo['Date'] = begins
				if str(year).isdigit(): vinfo['Year'] = year
				vinfo['Genre'] = 'Unterhaltung'
				vinfo['Studio'] = 'myspass.de'
				vinfo['Mediatype'] = cineType
				LSM.setInfo(type='Video', infoLabels=vinfo)
			LSM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
			if image and useThumbAsFanart and image != icon and not artpic in image:
				LSM.setArt({'fanart': image})
			if playType == 'single':
				LSM.setProperty('IsPlayable', 'true')
				LSM.setContentLookup(False)
			LSM.addContextMenuItems([(translation(30654), 'Action(Queue)')])
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LSM)
			SEND['videos'].append({'filter': episID, 'url': vidURL, 'tvshow': SERIE, 'name': name})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
	else:
		debug_MS("(navigator.listEpisodes) ##### Keine EPISODE-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30524), translation(30525).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### IDD = {IDD} ###")
	FINAL_URL, position = False, 0
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] != '00' and elem['filter'] == IDD:
				FINAL_URL = elem['url']
				seriesname = elem['tvshow']
				title = elem['name']
				title = title.split('[/COLOR]')[1].strip() if '[/COLOR]' in title else title
				debug_MS(f"(navigator.playCODE) ### WORKFILE-Line : {str(elem)} ###")
	if FINAL_URL:
		if '@@' in FINAL_URL:
			PLT, parts = cleanPlaylist(), FINAL_URL.split('@@')
			for each in parts:
				position += 1
				NRS_title = translation(30628).format(title, str(position), str(len(parts)))
				LVM = xbmcgui.ListItem(path=each, label=NRS_title)
				log(f"(navigator.playCODE) no. {str(position)}_playlist : {each}")
				PLT.add(each, LVM)
			xbmc.Player().play(PLT)
		else:
			log(f"(navigator.playCODE) StreamURL : {FINAL_URL} ")
			xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=FINAL_URL))
	else:
		failing("(navigator.playCODE) AbspielLink-00 : *MYSPASS* Der angeforderte -VideoLink- wurde NICHT gefunden !!!")
		return dialog.notification(translation(30521).format('Video'), translation(30526), icon, 8000)

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				debug_MS(f"(navigator.listShowsFavs) ### NAME : {name} || URL : {item.get('url')} || IMAGE : {logo} ###")
				addDir(name, logo, {'mode': 'listSeasons', 'url': item.get('url'), 'extras': logo, 'origSERIE': name}, FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30527), translation(30528).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30527), translation(30529).format(name), icon, 8000)

def addDir(name, image, params={}, plot=None, addType=0, FAVclear=False, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot)
	else:
		liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image and params.get('extras') != 'compilation':
		liz.setArt({'fanart': image})
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': params.get('origSERIE'), 'pict': 'None' if image == icon else image, 'url': params.get('url')}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url')}))])
	liz.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)
