# -*- coding: utf-8 -*-

from .common import *
from .references import Registration
from .utilities import Transmission


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def login_answer():
	NAME, USER, PWD = Registration().save_credentials()
	if Transmission().register_account(USER, PWD) is True:
		debug_MS("(navigator.login_answer) ##### ALLE DATEN GEFUNDEN - DIE ANMELDUNG WAR ERFOLGREICH #####")
		dialog.notification(translation(30528).format('LOGIN'), translation(30529).format(NAME), icon, 8000)
		return True
	else:
		debug_MS("(navigator.login_answer) ERROR - REGISTRATION - ERROR XXXXX !!! ANMELEDATEN ODER SERVER-ANTWORT FEHLERHAFT !!! XXXXX ")
		dialog.notification(translation(30521).format('LOGIN', ''), translation(30522), icon, 12000)
		return False

def create_account():
	debug_MS("(navigator.call_registration) ############### START ACCOUNT-REGISTRATION ###############")
	lastSTART = addon.getSetting('last_registstration')
	nowSTART = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
	if lastSTART != nowSTART:
		addon.setSetting('last_registstration', nowSTART)
	if Registration().clear_credentials() is True:
		if login_answer() is True:
			addon.setSetting('verified_account', 'true')
			xbmc.executebuiltin('Container.Refresh')
	else:
		debug_MS("(navigator.call_registration) XXXXX USER FORCE REMOVING ACCOUNT - ERROR // ERROR // ERROR XXXXX")
		dialog.notification(translation(30521).format('Account Bereinigung', ''), translation(30522), icon, 12000)

def erase_account():
	if Registration().clear_credentials(clearTries=True) is True:
		debug_MS("(navigator.destroy_account) XXXXX USER FORCE REMOVING ACCOUNT - DELETE ACCOUNTDATA - SUCCESS XXXXX")
		dialog.notification(translation(30528).format('Abmeldung und Daten löschen'), translation(30530), icon, 12000)
		xbmc.sleep(10000)
		xbmc.executebuiltin('Container.Refresh')
	else:
		debug_MS("(navigator.destroy_account) XXXXX USER FORCE REMOVING ACCOUNT - ERROR // ERROR // ERROR XXXXX")
		dialog.notification(translation(30521).format('Account Bereinigung', ''), translation(30522), icon, 12000)

def mainMenu():
	addDir(translation(30601), f"{artpic}favourites.png", {'mode': 'listFavorites'})
	addDir(translation(30602), icon, {'mode': 'listNewest'})
	addDir(translation(30603), icon, {'mode': 'listDates'})
	addDir(translation(30604), icon, {'mode': 'listStations'})
	addDir(translation(30605), icon, {'mode': 'listAlphabet'})
	addDir(translation(30606), icon, {'mode': 'listTopics'})
	addDir(translation(30607), icon, {'mode': 'listGenres'})
	addDir(translation(30608), icon, {'mode': 'listThemes'})
	addDir(translation(30609), f"{artpic}basesearch.png", {'mode': 'SearchRTLPLUS'})
	NAME, PWD = 'UNKNOWN', 'UNKNOWN'
	VERIFIED = False
	if Registration().has_credentials() is True and Transmission().verify_token() is True:
		(NAME, PWD), VERIFIED = Registration().get_credentials(), True
	if VERIFIED is True and addon.getSetting('login_status') in ['3', '2']:
		if (addon.getSetting('liveFree') == 'true' or addon.getSetting('livePay') == 'true'):
			addDir(translation(30610), f"{artpic}livestream.png", {'mode': 'listLivestreams'})
	addDir(translation(30611).format(str(cachePERIOD)), f"{artpic}remove.png", {'mode': 'clear_storage'}, folder=False)
	TEXTBOX = ""
	if VERIFIED is True and addon.getSetting('login_status') == '3': TEXTBOX = translation(30621).format(NAME)
	elif VERIFIED is True and addon.getSetting('login_status') == '2': TEXTBOX = translation(30621).format('FREE-USER')
	else: TEXTBOX = translation(30622)
	if enableADJUSTMENT:
		addDir(translation(30612)+TEXTBOX, f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30613), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	else:
		addDir(TEXTBOX, icon, {'mode': 'blankFUNC'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def load_pagination(ROUTE, POS):
	DATA_ONE = Transmission().makeREQUEST(f"{ROUTE}&page=1")
	if 'order=NameLong' in ROUTE and DATA_ONE.get('movies', '') and DATA_ONE.get('movies', {}).get('items', ''):
		DATA_ONE = DATA_ONE['movies']
	elif 'order=NameLong' in ROUTE and DATA_ONE.get('teaserSetInformations', '') and DATA_ONE.get('teaserSetInformations', {}).get('items', ''):
		DATA_ONE = DATA_ONE['teaserSetInformations']
	for item in DATA_ONE.get('items', []): yield item
	ALLPAGES = int(DATA_ONE.get('total', [])) // int(POS) if DATA_ONE.get('total', '') else -1
	debug_MS(f"(navigator.get_Pagination) ### Total-Items : {str(DATA_ONE.get('total', None))} || Result of PAGES : {str(ALLPAGES+1)} ###")
	for page in range(2, ALLPAGES+2, 1):
		debug_MS(f"(navigator.get_Pagination) ### NEW_URL : {ROUTE}&page={page} ###")
		DATA_TWO = Transmission().makeREQUEST(f"{ROUTE}&page={page}")
		if 'order=NameLong' in ROUTE and DATA_TWO.get('movies', '') and DATA_TWO.get('movies', {}).get('items', ''):
			DATA_TWO = DATA_TWO['movies']
		elif 'order=NameLong' in ROUTE and DATA_TWO.get('teaserSetInformations', '') and DATA_TWO.get('teaserSetInformations', {}).get('items', ''):
			DATA_TWO = DATA_TWO['teaserSetInformations']
		for item in DATA_TWO.get('items', []): yield item

def listSeries(url, POS, QUERY):
	debug_MS("(navigator.listSeries) ---------------------------------------- START = listSeries ----------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS(f"(navigator.listSeries) ### START_URL = {url} || NUMBERS = {POS} || QUERY = {unquote(QUERY)} ###")
	COMBI_SERIES = []
	UNIKAT = set()
	for serie in load_pagination(url, POS):
		COMBIstring, Note_1, Note_2, Note_3, Suffix_1 = ("" for _ in range(5))
		cover = None
		if 'format' in serie and 'teasersets/' in url:
			if serie.get('format', ''): serie = serie['format']
			else: continue
		if QUERY != 'None':
			COMBIstring = get_Description(serie, 'Series')
			COMBIstring += cleaning(serie['searchAliasName'].lower().replace(';', ','))
			COMBIstring += cleaning(serie['title'].lower())
		seriesID = serie.get('id', None)
		if seriesID is None or seriesID in UNIKAT:
			continue
		UNIKAT.add(seriesID)
		if serie.get('title', ''):
			title, seriesNAME = cleaning(serie['title']), cleaning(serie['title'])
		else: continue
		station = serie['station'].upper() if serie.get('station', '') else 'UNK'
		if 'format' in serie and not 'teasersets/' in url:
			serie = serie['format']
		genre = cleaning(serie['genre1']) if serie.get('genre1', '') else None
		image = (cleanPhoto(serie.get('formatimageMoviecover169', '')) or cleanPhoto(serie.get('formatimageArtwork', '')) or IMG_series.format(seriesID))
		category = serie.get('categoryId', 'episode')
		freeEP = serie.get('hasFreeEpisodes', True)
		if freeEP is False and STATUS < 3:
			Note_1   = seriesNAME
			Note_2   = '   [COLOR skyblue](premium)[/COLOR][CR][CR]'
			Suffix_1 = '     [COLOR deepskyblue](premium)[/COLOR]'
			if ONLY_FREE is True: continue
		Note_3 = get_Description(serie, 'Series') # Description of the Series
		name = title+Suffix_1
		plot = Note_1+Note_2+Note_3
		NOMEN, cineType = 'Series', 'episode'
		if category == 'film':
			NOMEN, cineType = 'Movies', 'movie'
			name = f"[I]{name}[/I]" if markMOVIES else name
			cover = IMG_coverdvd.format(seriesID)
		if QUERY != 'None' and unquote(QUERY).lower() in str(COMBIstring):
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listSeries[1]) ### Found in SEARCH (TITLE) : {seriesNAME} ###")
			debug_MS(f"(navigator.listSeries[1]) ### Found in SEARCH (STRING) : {str(COMBIstring)} ###")
			COMBI_SERIES.append([seriesID, name, seriesNAME, station, genre, image, cover, plot, NOMEN, cineType])
		elif QUERY == 'None':
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listSeries[1]) no.01 ##### seriesITEM : {str(serie)} #####")
			COMBI_SERIES.append([seriesID, name, seriesNAME, station, genre, image, cover, plot, NOMEN, cineType])
	if COMBI_SERIES:
		for seriesID, name, seriesNAME, station, genre, image, cover, plot, NOMEN, cineType in COMBI_SERIES:
			addType = 1
			if xbmcvfs.exists(watchFavsFile):
				with open(watchFavsFile, 'r') as fp:
					snippets = json.load(fp)
					for item in snippets.get('items', []):
						if item.get('url') == str(seriesID): addType = 2
			addDir(name, image, {'mode': 'listSeasons', 'url': str(seriesID), 'origSERIE': seriesNAME, 'photo': image, 'extras': NOMEN, 'type': cineType}, plot, genre=genre, studio=station, cover=cover, addType=addType)
			debug_MS("*****************************************")
			debug_MS(f"(navigator.listSeries[2]) ### SERIE : {seriesNAME} || seriesID : {str(seriesID)} || PHOTO : {image} || addType : {str(addType)} ###")
	elif not COMBI_SERIES and QUERY != 'None':
		return dialog.notification(translation(30525).format('Ergebnisse'), translation(30526), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(SERIES_idd, SERIES_img):
	debug_MS("(navigator.listSeasons) ---------------------------------------- START = listSeasons ----------------------------------------")
	COMBI_SEASON = []
	START_URL = f"{API_URL}/formats/{SERIES_idd}?fields=[%22id%22,%22title%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22tabSeason%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22genres%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22,%22onlineDate%22,%22annualNavigation%22,%22seasonNavigation%22]"
	try:
		DATA = Transmission().makeREQUEST(START_URL)
		debug_MS("++++++++++++++++++++++++")
		debug_MS(f"(navigator.listSeasons[1]) XXXXX CONTENT-01 : {str(DATA)} XXXXX")
		debug_MS("++++++++++++++++++++++++")
		seriesNAME = cleaning(DATA['title'])
	except: return dialog.notification(translation(30521).format('ID - ', SERIES_idd), translation(30524), icon, 8000)
	seasonID = str(DATA['id'])
	seasonPLOT = get_Description(DATA, 'Seasons')
	showSEA = DATA.get('tabSeason', False)
	seasonIMG = cleanPhoto(SERIES_img)
	if ((prefCONTENT == '0' or showSEA is False) and DATA.get('annualNavigation', '') and DATA.get('annualNavigation', {}).get('total', '') == 1) or ((prefCONTENT == '1' and showSEA is True) and DATA.get('seasonNavigation', '') and DATA.get('seasonNavigation', {}).get('total', '') == 1):
		debug_MS(f"(navigator.listSeasons[1]) ##### SERIE : {seriesNAME} || seasonID : {seasonID} || PHOTO : {str(seasonIMG)} #####")
		listEpisodes(seasonID, 'OneDirect', None)
	else:
		if (prefCONTENT == '0' or showSEA is False) and DATA.get('annualNavigation', '') and DATA.get('annualNavigation', {}).get('items', []):
			for each in DATA.get('annualNavigation', {}).get('items', []):
				PREFIX = 'Jahr '
				number = str(each['year'])
				debug_MS(f"(navigator.listSeasons[2]) ##### SERIE : {seriesNAME} || seasonID : {seasonID} || PHOTO : {str(seasonIMG)} || YEAR : {number} #####")
				COMBI_SEASON.append([seasonID, PREFIX, number, seasonPLOT, seasonIMG, seriesNAME])
		elif (prefCONTENT == '1' and showSEA is True) and DATA.get('seasonNavigation', '') and DATA.get('seasonNavigation', {}).get('items', []):
			for each in DATA.get('seasonNavigation', {}).get('items', []):
				PREFIX = 'Staffel '
				number = str(each['season'])
				debug_MS(f"(navigator.listSeasons[2]) ##### SERIE : {seriesNAME} || seasonID : {seasonID} || PHOTO : {str(seasonIMG)} || SEASON : {number} #####")
				COMBI_SEASON.append([seasonID, PREFIX, number, seasonPLOT, seasonIMG, seriesNAME])
	if COMBI_SEASON:
		COURSE = True if SORTING == '0' else False
		for seasonID, PREFIX, number, seasonPLOT, seasonIMG, seriesNAME in sorted(COMBI_SEASON, key=lambda n:n[2].zfill(2), reverse=COURSE):
			name = translation(30623) if number == '0' else PREFIX+number
			addDir(name, seasonIMG, {'mode': 'listEpisodes', 'url': seasonID, 'origSERIE': seriesNAME, 'extras': PREFIX+number}, seasonPLOT, addType=2)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(SEASON_idd, SEASON_plus, EPIS_idd):
	debug_MS("(navigator.listEpisodes) ---------------------------------------- START = listEpisodes ----------------------------------------")
	SEND, REAR = {}, False
	COMBI_EPISODE, SEND['videos'] = ([] for _ in range(2))
	ENTRIES = '[%22id%22,%22title%22,%22broadcastStartDate%22,%22catchupStartDate%22,%22availableDate%22,%22catchupEndDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,'\
						'%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20asc'
	if SEASON_plus not in ['standard', 'OneDirect']:
		if 'Jahr ' in SEASON_plus or len(SEASON_plus) == 4:
			YEAR_clear = SEASON_plus.split('Jahr ')[1] if 'Jahr' in SEASON_plus else SEASON_plus
			START_URL = f"{API_URL}/movies?filter={{%22BroadcastStartDate%22:{{%22between%22:{{%22start%22:%22{YEAR_clear}-01-01%2000:00:00%22,%22end%22:%22{YEAR_clear}-12-31%2023:59:59%22}}}},%22FormatId%22:{SEASON_idd}}}&fields={ENTRIES}"
		elif 'Staffel ' in SEASON_plus:
			SEASON_clear = SEASON_plus.split('Staffel ')[1]
			START_URL = f"{API_URL}/movies?filter={{%22Season%22:{SEASON_clear},%22FormatId%22:{SEASON_idd}}}&fields={ENTRIES}"
	elif SEASON_plus == 'OneDirect':
		START_URL = f"{API_URL}/movies?filter={{%22FormatId%22:{SEASON_idd}}}&fields={ENTRIES}"
	else:
		START_URL = SEASON_idd
	debug_MS(f"(navigator.listEpisodes[1]) XXXXX SEASON_idd = {SEASON_idd} || SEASON_plus = {SEASON_plus} || EPIS_idd = {EPIS_idd} || START_URL = {START_URL} XXXXX")
	DATA = Transmission().makeREQUEST(START_URL)
	if DATA.get('movies', '') and DATA.get('movies', {}).get('items', ''):
		DATA = DATA['movies']
	for vid in DATA.get('items', []):
		background, station, category, Note_1, Note_2, Note_3, Note_4, Note_5, Note_6, Suffix_1, Suffix_2 = ("" for _ in range(11))
		tagline, seriesname, genre, season, episode, streamSD, streamHD, startTIMES, startTITLE, begins, endTIMES, mpaa, year, cover = (None for _ in range(14))
		genreLIST = []
		episID = str(vid.get('id', '00'))
		title = cleaning(vid['title'])
		tagline = cleaning(vid.get('teaserText', ''))
		duration = get_RunTime(vid['duration']) if vid.get('duration', '') else '0'
		if vid.get('format', ''):
			SHORT = vid['format']
			seriesname = cleaning(SHORT['title']) if SHORT.get('title', '') else None
			if seriesname is None: seriesname = cleaning(SHORT['seoUrl']).replace('-', ' ').title() if SHORT.get('seoUrl', '') else None
			if seriesname is None: continue
			background = (cleanPhoto(SHORT.get('formatImageClear', '')) or cleanPhoto(SHORT.get('formatimageArtwork', '')) or cleanPhoto(SHORT.get('defaultImage169Logo', '')))
			station = SHORT['station'].upper() if SHORT.get('station', '') else 'UNK'
			if SHORT.get('genres', ''):
				genreLIST = [cleaning(gen) for gen in SHORT.get('genres', '')]
				if genreLIST: genre = ' / '.join(sorted(genreLIST))
			if genre is None and SHORT.get('genre1', ''):
				genre = cleaning(SHORT['genre1'])
			category = SHORT.get('categoryId', '')
		else: continue
		debug_MS("---------------------------------------------")
		debug_MS(f"(navigator.listEpisodes[2]) ##### EPISODE-02 : {str(vid)} #####")
		protect = vid.get('isDrm', False)
		PayFree = (vid.get('payed', True) or vid.get('free', True))
		if PayFree is False and vodPremium is False and STATUS < 3:
			Note_1   = translation(30624).format(seriesname)
			Note_2   = '   [COLOR skyblue](premium)[/COLOR][CR]'
			Suffix_2 = '     [COLOR deepskyblue](premium)[/COLOR]'
			if ONLY_FREE is True: continue
		else: Note_1 = translation(30624).format(seriesname)+'[CR]'
		season = re.sub('[a-zA-Z]', '', str(vid['season'])).zfill(2) if vid.get('season', '') else None
		episode = re.sub('[a-zA-Z]', '', str(vid['episode'])).zfill(2) if vid.get('episode', '') else None
		if season and episode: Note_3 = translation(30625).format(season, episode)
		elif season is None and episode: Note_3 = translation(30626).format(episode)
		if vid.get('manifest', '') and vid['manifest'].get('dash', ''): # Normal-Play with Pay-Account
			# https://vodnowusoawsdash-a.akamaihd.net/p112/manifest/rtlplushd/5907675-1/10000.ism/.mpd
			streamSD = vid['manifest']['dash'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').replace('/p11114', '/p112').replace('manifest/tvnow', 'manifest/rtlplussd').replace('/0.ism', '/4000.ism').replace('/10000.ism', '/4000.ism').split('.mpd')[0]+'.mpd'
		if vid.get('manifest', '') and vid['manifest'].get('dashhd', ''): # HD-Play with Pay-Account
			# https://vodnowusoawsdash-a.akamaihd.net/p112/manifest/rtlplussd/5907675-1/4000.ism/.mpd
			streamHD = vid['manifest']['dashhd'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').replace('/p11114', '/p112').replace('manifest/tvnow', 'manifest/rtlplushd').replace('/0.ism', '/10000.ism').replace('/4000.ism', '/10000.ism').split('.mpd')[0]+'.mpd'
		STARTS = (vid.get('broadcastStartDate', None) or vid.get('catchupStartDate', None))
		if str(STARTS)[:4].isdigit() and str(STARTS)[:4] not in ['0', '1970']:
			broadcast = datetime(*(time.strptime(STARTS[:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2015-10-07 05:10:00
			startTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			for sd in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))): startTIMES = startTIMES.replace(*sd)
			startTITLE = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			begins = broadcast.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
			if KODI_ov20:
				begins = broadcast.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
		ENDS = (vid.get('catchupEndDate', None) or vid.get('availableDate', None))
		if str(ENDS)[:4].isdigit() and str(ENDS)[:4] not in ['0', '1970']:
			available = datetime(*(time.strptime(ENDS[:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2025-01-01 06:00:00
			endTIMES = available.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			for ed in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))): endTIMES = endTIMES.replace(*ed)
		Note_4 = translation(30627).format(str(startTIMES)) if startTIMES else ""
		if showDATE and startTITLE:
			Suffix_1 = translation(30628).format(str(startTITLE))
		if endTIMES and PayFree is True and STATUS < 3 and datetime.now() < available:
			Note_5 = translation(30629).format(str(endTIMES))
		else: Note_5 = '[CR]'
		if str(vid.get('fsk')).isdigit():
			mpaa = translation(30630).format(str(vid['fsk'])) if str(vid.get('fsk')) != '0' else translation(30631)
		if str(vid.get('productionYear'))[:4].isdigit() and str(vid.get('productionYear'))[:4] not in ['0', '1970']:
			year = str(vid['productionYear'])[:4]
		# BILD_1 = https://aistvnow-a.akamaihd.net/tvnow/movie/1454577/960x0/image.jpg
		# BILD_2 = https://ais.tvnow.de/tvnow/movie/1454577/960x0/image.jpg
		cineType = 'movie' if category == 'film' else 'episode'
		if cineType == 'movie' and SEASON_plus != 'standard':
			cover = IMG_coverdvd.format(SEASON_idd)
		image = IMG_movies.format(episID)
		Note_6 = get_Description(vid) # Description of the Video
		uvz = build_mass({'mode': 'playDash', 'xcode': episID})
		name = title+Suffix_1+Suffix_2
		plot = Note_1+Note_2+Note_3+Note_4+Note_5+Note_6
		SEND['videos'].append({'filter': episID, 'stored': EPIS_idd, 'name': name, 'photo': image, 'streamSD': streamSD, 'streamHD': streamHD, 'description': plot, 'channel': station, 'secureDRM': protect, 'payfree': PayFree})
		COMBI_EPISODE.append([episID, EPIS_idd, season, episode, seriesname, name, streamSD, streamHD, uvz, tagline, plot, duration, begins, year, genre, station, mpaa, cineType, image, cover, background, protect, PayFree])
	if COMBI_EPISODE:
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		if EPIS_idd is not None and len(EPIS_idd) > 4:
			parts = COMBI_EPISODE[:]
			matching = [obj for obj in parts if obj[0] == obj[1]]
			if matching:
				debug_MS(f"(navigator.listEpisodes[3]) ##### MATCH FOR MEDIALIBRARY : {matching} #####")
				return playDash('DEFAULT', matching, None, None, None, 'UNK')
		else:
			for episID, EPIS_idd, season, episode, seriesname, name, streamSD, streamHD, uvz, tagline, plot, duration, begins, year, genre, station, mpaa, cineType, image, cover, background, protect, PayFree in COMBI_EPISODE:
				for method in get_Sorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
				debug_MS("*****************************************")
				debug_MS(f"(navigator.listEpisodes[3]) ##### NAME : {name} || IDD : {str(episID)} || GENRE : {str(genre)} || DURATION: {str(duration)} #####")
				debug_MS(f"(navigator.listEpisodes[3]) ##### SERIE : {str(seriesname)} || SEASON : {str(season)} || EPISODE : {str(episode)} || YEAR : {str(year)} || MPAA : {str(mpaa)} #####")
				debug_MS(f"(navigator.listEpisodes[3]) ##### IMAGE : {image} || STUDIO : {station} || TYPE : {cineType} #####")
				LEM = xbmcgui.ListItem(name)
				if plot in ['', 'None', None]: plot = "..."
				if KODI_ov20:
					vinfo = LEM.getVideoInfoTag()
					if str(season).isdigit(): vinfo.setSeason(int(season))
					if str(episode).isdigit(): vinfo.setEpisode(int(episode))
					vinfo.setTvShowTitle(seriesname)
					vinfo.setTitle(name)
					vinfo.setTagLine(tagline)
					vinfo.setPlot(plot)
					if str(duration).isdigit(): vinfo.setDuration(int(duration))
					if begins: LEM.setDateTime(begins)
					if str(year).isdigit(): vinfo.setYear(int(year))
					if genre and len(genre) > 4: vinfo.setGenres([genre])
					vinfo.setStudios([station])
					vinfo.setMpaa(mpaa)
					vinfo.setMediaType(cineType)
				else:
					vinfo = {}
					if str(season).isdigit(): vinfo['Season'] = season
					if str(episode).isdigit(): vinfo['Episode'] = episode
					vinfo['TvShowTitle'] = seriesname
					vinfo['Title'] = name
					vinfo['Tagline'] = tagline
					vinfo['Plot'] = plot
					if str(duration).isdigit(): vinfo['Duration'] = duration
					if begins: vinfo['Date'] = begins
					if str(year).isdigit(): vinfo['Year'] = year
					if genre and len(genre) > 4: vinfo['Genre'] = genre
					vinfo['Studio'] = station
					vinfo['Mpaa'] = mpaa
					vinfo['Mediatype'] = cineType
					LEM.setInfo('Video', vinfo)
				LEM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
				if cover:
					LEM.setArt({'poster': cover})
				if useSerieAsFanart and background != "":
					LEM.setArt({'fanart': background})
					REAR = True
				if not REAR and image and image != icon and not artpic in image:
					LEM.setArt({'fanart': image})
				LEM.setProperty('IsPlayable', 'true')
				LEM.setContentLookup(False)
				LEM.addContextMenuItems([(translation(30654), 'Action(Queue)')])
				xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LEM)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listNewest():
	debug_MS("(navigator.listNewest) ****************************************** START = listNewest > GO TO listEpisodes ******************************************")
	BEFORE = (datetime.now() - timedelta(days=2)).strftime('%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))
	NOW = datetime.now().strftime('%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))
	ENTRIES = '[%22id%22,%22title%22,%22broadcastStartDate%22,%22catchupStartDate%22,%22availableDate%22,%22catchupEndDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,'\
						'%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20desc'
	NEW_URL = f"{API_URL}/movies?filter={{%22BroadcastStartDate%22:{{%22between%22:{{%22start%22:%22{BEFORE.replace('T', '%20')}%22,%22end%22:%22{NOW.replace('T', '%20')}%22}}}}}}&fields={ENTRIES}"
	listEpisodes(NEW_URL, 'standard', None)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDates():
	debug_MS("(navigator.listDates) ---------------------------------------- START = listDates ----------------------------------------")
	for ii in range(-7, 8, 1):
		WU = (datetime.now() - timedelta(days=ii)).strftime('%Y{0}%m{0}%d'.format('-'))
		WT = (datetime.now() - timedelta(days=ii)).strftime('%a{0}%d{1} %b'.format('~', '.'))
		MD = WT.split('~')[0].replace('Mon', translation(32101)).replace('Tue', translation(32102)).replace('Wed', translation(32103)).replace('Thu', translation(32104)).replace('Fri', translation(32105)).replace('Sat', translation(32106)).replace('Sun', translation(32107))
		MM = WT.split('~')[1].replace('Mar', translation(32201)).replace('May', translation(32202)).replace('Oct', translation(32203)).replace('Dec', translation(32204))
		ENTRIES = '[%22id%22,%22title%22,%22broadcastStartDate%22,%22catchupStartDate%22,%22availableDate%22,%22catchupEndDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,'\
							'%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20asc'
		NEW_URL = f"{API_URL}/movies?filter={{%22BroadcastStartDate%22:{{%22between%22:{{%22start%22:%22{WU}%2000:00:01%22,%22end%22:%22{WU}%2023:59:59%22}}}}}}&fields={ENTRIES}"
		if ii == 0: addDir(f"[B][COLOR lime]{MM} | {MD}[/COLOR][/B]", icon, {'mode': 'listEpisodes', 'url': NEW_URL})
		else: addDir(f"{MM} | {MD}", icon, {'mode': 'listEpisodes', 'url': NEW_URL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listStations():
	debug_MS("(navigator.listStations) ---------------------------------------- START = listStations ----------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	COMBI_CHANNEL = [{'id': 'geo', 'name': 'GEO Television'}, {'id': 'nitro', 'name': 'NITRO'}, {'id': 'nowus', 'name': 'NOW!'},
		{'id': 'ntv', 'name': 'ntv'}, {'id': 'rtl', 'name': 'RTL'}, {'id': 'crime', 'name': 'RTL Crime'},{'id': 'living', 'name': 'RTL Living'}, 
		{'id': 'passion', 'name': 'RTL Passion'}, {'id': 'rtl2', 'name': 'RTLZWEI'}, {'id': 'rtlplus', 'name': 'RTLup'}, {'id': 'superrtl', 'name': 'Super RTL'}, 
		{'id': 'toggoplus', 'name': 'TOGGO plus'}, {'id': 'vox', 'name': 'VOX'},  {'id': 'voxup', 'name': 'VOXup'}, {'id': 'tvnow', 'name': 'TVNOW'},
		{'id': 'tvnowkids', 'name': 'TVNOW Kids'}, {'id': 'watchbox', 'name': 'WATCHBOX'}]
	for chan in COMBI_CHANNEL:
		NEW_URL = f"{API_URL}/formats?filter={{%22Disabled%22:%220%22,%22Station%22:%22{chan['id']}%22}}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc"
		addDir(chan['name'], f"{stapic}{chan['id']}.png", {'mode': 'listSeries', 'url': NEW_URL, 'extras': 500})
		debug_MS(f"(navigator.listStations[1]) ### NAME : {chan['name']} || stationID : {chan['id']} || LOGO : {stapic}{chan['id']}.png ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ---------------------------------------- START = listAlphabet ----------------------------------------")
	for letter in ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
		NEW_URL = f"{API_URL}/formats?filter={{%22Disabled%22:%220%22,%22TitleGroup%22:%22{letter}%22}}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc"
		addDir(letter, f"{alppic}{letter}.jpg", {'mode': 'listSeries', 'url': NEW_URL, 'extras': 500})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTopics():
	debug_MS("(navigator.listTopics) ---------------------------------------- START = listTopics ----------------------------------------")
	UN_Supported = ['11649', '11650', '11652', '11664', '11668', '11670', '11692', '11695', '11734', '11758', '11759', '11790', '11994',
		'12427', '12521', '12616', '12627', '12677', '12678', '12775', '12815', '12895', '12924', '12930', '12994', '13044', '13084', '13175',
		'13183', '13411', '13747', '13757', '13787', '13793', '14027', '14029', '14062', '14064', '14438']
	DATA = Transmission().makeREQUEST(f"{API_URL}/pages/nowtv/home-v1?fields=teaserSets.headline,teaserSets.id")
	for top in DATA['teaserSets']['items']:
		topicID = str(top['id'])
		name = cleaning(top['headline'])
		if not any(x in topicID for x in UN_Supported):
			NEW_URL = f"{API_URL}/teasersets/{topicID}?fields=[%22teaserSetInformations%22,[%22format%22,[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]]]&maxPerPage=100&order=NameLong%20asc"
			addDir(name, icon, {'mode': 'listSeries', 'url': NEW_URL, 'extras': 100})
			debug_MS(f"(navigator.listTopics[1]) ### topicID : {topicID} || NAME : {name} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listGenres():
	debug_MS("(navigator.listGenres) ---------------------------------------- START = listGenres ----------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	DATA = Transmission().makeREQUEST(f"{API_URL}/genres?maxPerPage=100")
	for genre in DATA['items']:
		name = cleaning(genre['name'])
		seoUrl = genre['seoUrl']
		tagline = cleaning(genre['description'])
		NEW_URL = f"{API_URL}/formats/genre/{seoUrl.replace('-','%20')}?filter={{%22station%22:%22none%22}}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc"
		logo = f"{genpic}{name}.png" if xbmcvfs.exists(f"{genpic}{name}.png") else icon
		addDir(name, logo, {'mode': 'listSeries', 'url': NEW_URL, 'extras': 500}, tagline=tagline)
		debug_MS(f"(navigator.listGenres[1]) ### genreNAME : {name} || NEW_URL : {NEW_URL} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listThemes():
	debug_MS("(navigator.listThemes) ---------------------------------------- START = listThemes ----------------------------------------")
	ENTRIES = '[%22id%22,%22title%22,%22broadcastStartDate%22,%22catchupStartDate%22,%22availableDate%22,%22catchupEndDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,'\
						'%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=100'
	# https://api.tvnow.de/v3/channels/station/rtl?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500&page=1
	DATA = Transmission().makeREQUEST(f"{API_URL}/channels/station/rtl?fields=*&filter={{%22Active%22:true}}&maxPerPage=100")
	for theme in DATA['items']:
		themeID = str(theme['id'])
		name = cleaning(theme['title'])
		logo = f"https://aistvnow-a.akamaihd.net/tvnow/cms/{theme['portraitImage']}/image.jpg"
		NEW_URL = f"{API_URL}/channels/{themeID}/movies?filter={{%22station%22:%22none%22}}&fields={ENTRIES}"
		addDir(name, logo, {'mode': 'listEpisodes', 'url': NEW_URL})
		debug_MS(f"(navigator.listThemes[1]) ### themeID : {themeID} || NAME : {name} || PHOTO : {logo} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchRTLPLUS():
	debug_MS("(navigator.SearchRTLPLUS) ---------------------------------------- START = SearchRTLPLUS ----------------------------------------")
	keyword = None
	if xbmcvfs.exists(SEARCHFILE):
		with open(SEARCHFILE, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30632), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword:
			keyword = quote(keyword)
			with open(SEARCHFILE, 'w') as record:
				record.write(keyword)
	if keyword:
		NEW_URL = f"{API_URL}/formats?fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22searchAliasName%22,%22metaTags%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500"
		return listSeries(NEW_URL, 500, keyword)
	return None

def listLivestreams():
	debug_MS("(navigator.listLivestreams) ---------------------------------------- START = listLivestreams ----------------------------------------")
	SEND = {}
	SEND['videos'], COMBI_STATIONS = ([] for _ in range(2))
	if liveGratis is False and livePremium is False:
		failing("(navigator.listLivestreams[00]) ##### Sie haben KEINE Berechtigung : Für LIVE-TV ist ein Premium-Account Voraussetzung !!! #####")
		return dialog.notification(translation(30532), translation(30533), icon, 12000)
	DATA = Transmission().retrieveCONTENT(f"{API_URL}/epgs/movies/nownext?fields=nowNextEpgMovies.*")
	for channel in DATA['items']:
		debug_MS("---------------------------------------------")
		debug_MS(f"(navigator.listLivestreams[1]) ##### CHANNEL-01 : {str(channel)} #####")
		title, subTitle, title_2, subTitle_2, plot = ("" for _ in range(5))
		START, START_2, END, END_2, streamSD, streamHD = (None for _ in range(6))
		SHORT = channel['nowNextEpgMovies']['items'][0]
		station = cleaning(SHORT['station']).upper().replace('RTLPLUS', 'RTLUP').replace('RTL2', 'RTLZWEI')
		SORTING_TITLE = station.replace('CRIME', 'RTLCRIME').replace('LIVING', 'RTLLIVING').replace('PASSION', 'RTLPASSION')
		VIDEO_CHAN = station.lower().replace('crime', 'rtlcrime').replace('living', 'rtlliving').replace('passion', 'rtlpassion').replace('nowus', 'now').replace('rtlzwei', 'rtl2')
		liveID = str(SHORT['id'])
		title = cleaning(SHORT.get('title', ''))
		subTitle = cleaning(SHORT.get('subTitle', ''))
		if title == "" and subTitle != "":
			title = subTitle
		elif title != "" and subTitle != "":
			title = f"{title} - {subTitle}"
		if str(SHORT.get('startDate'))[:4].isdigit():
			startDT = datetime(*(time.strptime(SHORT['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			START = startDT.strftime('{0}%H{1}%M').format('(', ':')
		if str(SHORT.get('endDate'))[:4].isdigit():
			endDT = datetime(*(time.strptime(SHORT['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			END = endDT.strftime(' {0} %H{1}%M{2}').format('-', ':', ')')
		photo = IMG_tvepg.format(liveID)
		if END: plot = translation(30633).format(END.replace('-', '').replace(')', '').strip())
		if channel.get('nowNextEpgMovies', {}).get('total', '') == 2:
			BRIEF = channel['nowNextEpgMovies']['items'][1]
			title_2 = cleaning(BRIEF.get('title', ''))
			subTitle_2 = cleaning(BRIEF.get('subTitle', ''))
			if title_2 == "" and subTitle_2 != "":
				title_2 = subTitle_2
			elif title_2 != "" and subTitle_2 != "":
				title_2 = f"{title_2} - {subTitle_2}"
			if str(BRIEF.get('startDate'))[:4].isdigit():
				startDT_2 = datetime(*(time.strptime(BRIEF['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				START_2 = startDT_2.strftime('%H{0}%M').format(':')
			if str(BRIEF.get('endDate'))[:4].isdigit():
				endDT_2 = datetime(*(time.strptime(BRIEF['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				END_2 = endDT_2.strftime('%H{0}%M').format(':')
			if START_2 and END_2:
				plot += translation(30634).format(title_2, START_2, END_2)
		name = translation(30635).format(station, title)
		if START and END:
			name = translation(30636).format(station, title, START+END)
		streamSD = f"https://pnowlive-a.akamaized.net/live/{VIDEO_CHAN}/dash/{VIDEO_CHAN}.mpd"
		streamHD = f"https://pnowlive-a.akamaized.net/live/{VIDEO_CHAN}hd/dash/{VIDEO_CHAN}hd.mpd"
		# NEW(hd) = https://p-nowlive.secure.footprint.net/live/rtlhd/dash/rtlhd.mpd // Juni.2023
		# NEW(sd) = https://pnowlive-a.akamaized.net/live/rtl/dash/rtl.mpd // Juli.20222
		SEND['videos'].append({'filter': liveID, 'stored': None, 'name': name, 'photo': photo, 'streamSD': streamSD, 'streamHD': streamHD, 'description': plot, 'channel': station, 'secureDRM': True, 'payfree': False})
		COMBI_STATIONS.append([liveID, SORTING_TITLE, name, streamSD, streamHD, photo, plot, station])
	if COMBI_STATIONS:
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		for liveID, SORTING_TITLE, name, streamSD, streamHD, photo, plot, station in sorted(COMBI_STATIONS, key=lambda n: n[1], reverse=False):
			addDir(name, photo, {'mode': 'playDash', 'action': 'LIVE', 'xcode': liveID}, plot, studio=station, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def playDash(action, xcode, xlink, xdrm, xfree, xtele):
	debug_MS("(navigator.playDash) ---------------------------------------- START = playDash ----------------------------------------")
	VERIFIED = Transmission().verify_token()
	addon.setSetting('high_definition', 'true') if VERIFIED is True and addon.getSetting('login_status') == '3' and addon.getSetting('force_best') == '0' else addon.setSetting('high_definition', 'false')
	choosingHD = (True if addon.getSetting('high_definition') == 'true' else False)
	ACCESS_TOKEN = addon.getSetting('authtoken') if addon.getSetting('authtoken').startswith('eyJ') else '0'
	UAG = f"User-Agent={get_userAgent()}&Referer=https://plus.rtl.de/"
	FOUND, streamLOW, streamHIGH, SELECTION, secureDRM, PAYFREE, CHANNEL, FINAL_URL = (False for _ in range(8))
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	if action == 'IPTV' and xlink:
		SELECTION, secureDRM, PAYFREE, CHANNEL = xlink, xdrm, xfree, xtele
		if livePremium is False and (STATUS < 3 or ACCESS_TOKEN == '0'):
			xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(path=SELECTION))
			failing("(navigator.playDash[00]) ##### Sie haben KEINE Berechtigung : Diese LIVE-TV-Sendung ist nur mit einem Premium-Account abspielbar !!! #####")
			return dialog.notification(translation(30532), translation(30534), icon, 12000)
		else:
			FOUND, FINAL_URL = True, SELECTION
	elif action in ['DEFAULT', 'LIVE'] and xcode:
		with open(WORKFILE, 'r') as wok:
			ARRIVE = json.load(wok)
			for elem in ARRIVE['videos']:
				if elem['filter'] != '00' and (elem['filter'] == xcode or elem['filter'] == elem['stored']):
					TITLE = elem['name']
					PHOTO = elem['photo']
					streamLOW = elem['streamSD']
					streamHIGH = elem['streamHD']
					PLOT = elem['description']
					CHANNEL = elem['channel']
					secureDRM = elem['secureDRM']
					PAYFREE = elem['payfree']
					debug_MS(f"(navigator.playDash[1]) ### WORKFILE-Line : {str(elem)} ###")
		if streamLOW or streamHIGH:
			lowQUALITY = True if streamLOW else False
			if streamHIGH and (choosingHD is True or lowQUALITY is False): # High Quality
				SELECTION = streamHIGH
			if lowQUALITY is True and SELECTION is False: # Lower Quality
				SELECTION = streamLOW
			if action == 'DEFAULT' and ACCESS_TOKEN != '0' and SELECTION and ((vodPremium is True and STATUS == 3) or (PAYFREE is True)):
				FOUND, FINAL_URL = True, SELECTION
			elif action == 'DEFAULT' and vodPremium is False and (STATUS < 3 or ACCESS_TOKEN == '0'):
				xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem(path=SELECTION))
				xbmc.PlayList(1).clear()
				failing("(navigator.playDash[00]) ##### Sie haben KEINE Berechtigung : Dieser VoD-Stream ist nur mit einem Premium-Account abspielbar !!! #####")
				return dialog.ok(addon_id, translation(30504))
			elif action == 'LIVE' and livePremium is True and STATUS == 3 and ACCESS_TOKEN != '0':
				FOUND, FINAL_URL = True, SELECTION
			elif action == 'LIVE' and livePremium is False and (STATUS < 3 or ACCESS_TOKEN == '0'):
				failing("(navigator.playDash[00]) ##### Sie haben KEINE Berechtigung : Diese LIVE-TV-Sendung ist nur mit einem Premium-Account abspielbar !!! #####")
				return dialog.notification(translation(30532), translation(30534), icon, 8000)
	debug_MS("*****************************************")
	debug_MS(f"(navigator.playDash[1]) ### ACTION : {str(action)} || XLINK : {str(SELECTION)} || XTELE : {str(CHANNEL)} ###")
	debug_MS(f"(navigator.playDash[1]) ### XCODE : {str(xcode)} || XDRM : {str(secureDRM)} || XFREE : {str(PAYFREE)} ###")
	debug_MS(f"(navigator.playDash[1]) ### FINAL_URL : {str(FINAL_URL)} || FOUND : {str(FOUND)} || choosingHD : {str(choosingHD)} ###")
	if FOUND is True and FINAL_URL:
		log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FINAL_URL !!! GEFUNDEN @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		LSM = xbmcgui.ListItem(path=FINAL_URL)
		log(f"(navigator.playDash) StreamURL : {FINAL_URL}")
		LSM.setMimeType('application/dash+xml')
		LSM.setProperty('inputstream', 'inputstream.adaptive')
		if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
			LSM.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		if KODI_ov20:
			LSM.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={get_userAgent()}") # On KODI v20 and above
		else:
			LSM.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={get_userAgent()}") # On KODI v19 and below
		if secureDRM in ['True', True]:
			debug_MS(f"(navigator.playDash[2]) ### ACCESS_TOKEN-02 : {str(ACCESS_TOKEN)} ###")
			LSM.setProperty('inputstream.adaptive.license_key', LICENSE_URL.format(UAG, ACCESS_TOKEN, 'R{SSM}'))
			LSM.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
			debug_MS("(navigator.playDash[2]) ### LICENSE_URL : "+LICENSE_URL.format(UAG, ACCESS_TOKEN, 'R{SSM}')+" ###")
		if action in ['IPTV', 'LIVE']:
			if KODI_un21: # THE "full" BEHAVIOUR PARAM HAS BEEN REMOVED ON Kodi v21 because now enabled by default.
				LSM.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
			if action == 'IPTV':
				LSM.setProperty('IsPlayable', 'true')
				LSM.setContentLookup(False)
				if KODI_ov20:
					vinfo = LSM.getVideoInfoTag()
					vinfo.setTitle(f"Livestream - {CHANNEL}"), vinfo.setStudios([CHANNEL])
				else:
					LSM.setInfo('Video', {'Title': f"Livestream - {CHANNEL}", 'Studio': CHANNEL})
			elif action =='LIVE':
				if KODI_ov20:
					vinfo = LSM.getVideoInfoTag()
					vinfo.setTitle(TITLE), vinfo.setPlot(PLOT), vinfo.setStudios([CHANNEL])
				else:
					LSM.setInfo('Video', {'Title': TITLE, 'Plot': PLOT, 'Studio': CHANNEL})
				LSM.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO, 'fanart': defaultFanart})
				xbmc.Player().play(item=FINAL_URL, listitem=LSM)
		if action in ['DEFAULT', 'IPTV']:
			xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		xbmc.sleep(5000)
		if not xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)') and not xbmc.Player().isPlaying():
			return dialog.notification(translation(30521).format('DASH - URL', ''), translation(30536), icon, 8000)

def listFavorites():
	debug_MS("(navigator.listFavorites) ---------------------------------------- START = listFavorites ----------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(watchFavsFile):
		with open(watchFavsFile, 'r') as fp:
			snippets = json.load(fp)
			for item in snippets.get('items', []):
				title = f"[I]{cleaning(item.get('name'))}[/I]" if markMOVIES and item.get('type') == 'movie' else cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else cleanPhoto(item.get('pict'))
				addDir(title, logo, {'mode': 'listSeasons', 'url': item.get('url'), 'origSERIE': cleaning(item.get('name')), 'photo': logo, 'type': item.get('type')}, cleaning(item.get('plot')), FAVclear=True)
				debug_MS(f"(navigator.listFavorites[1]) ### NAME : {title} || URL : {item.get('url')} || IMAGE : {logo} || cineType : {item.get('type')} ###")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(watchFavsFile):
		with open(watchFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'type': type})
		with open(watchFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30537), translation(30538).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(watchFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30537), translation(30539).format(name), icon, 8000)

def addDir(name, image, params={}, plot=None, tagline=None, genre=None, studio=None, cover=None, addType=0, FAVclear=False, folder=True):
	uws, entries = build_mass(params), []
	LDM = xbmcgui.ListItem(name)
	if plot in ['', 'None', None]: plot = "..."
	if KODI_ov20:
		vinfo = LDM.getVideoInfoTag()
		vinfo.setTitle(name)
		vinfo.setTagLine(tagline)
		vinfo.setPlot(plot)
		if genre and len(genre) > 4: vinfo.setGenres([genre])
		vinfo.setStudios([studio])
	else:
		vinfo = {}
		vinfo['Title'] = name
		vinfo['Tagline'] = tagline
		vinfo['Plot'] = plot
		if genre and len(genre) > 4: vinfo['Genre'] = genre
		vinfo['Studio'] = studio
		LDM.setInfo('Video', vinfo)
	LDM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if cover:
		LDM.setArt({'poster': cover})
	if image and image != icon and not artpic in image:
		LDM.setArt({'fanart': image})
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'ADD', 'name': params.get('origSERIE'), 'pict': 'None' if image == icon else image, 'url': params.get('url'),
			'plot': plot.replace('\n', '[CR]'), 'type': params.get('type')}))])
	if addType in [1, 2] and enableLIBRARY:
		entries.append([translation(30653), 'RunPlugin({})'.format(build_mass({'mode': 'preparefiles', 'url': params.get('url'), 'name': params.get('origSERIE'), 'extras': params.get('extras'), 'cycle': libraryPERIOD}))])
	if addType == 0 and FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({})'.format(build_mass({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), 'plot': plot, 'type': params.get('type')}))])
	LDM.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uws, listitem=LDM, isFolder=folder)
