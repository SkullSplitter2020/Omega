# -*- coding: utf-8 -*-

from .common import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

def mainMenu():
	addDir(translation(30601), icon, {'mode': 'blankFUNC', 'url': '00'}, folder=False)
	addDir(translation(30602), icon, {'mode': 'trailers', 'target': 'MOVIES'})
	addDir(translation(30603), icon, {'mode': 'movies'})
	addDir(translation(30604), icon, {'mode': 'blankFUNC', 'url': '00'}, folder=False)
	addDir(translation(30605), icon, {'mode': 'trailers', 'target': 'SERIES'})
	addDir(translation(30606), icon, {'mode': 'series'})
	addDir(translation(30607), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/interviews/", 'target': 'INTERVIEWS'})
	if enableADJUSTMENT:
		addDir(translation(30608), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def trailers(CATEGORY):
	if CATEGORY == 'MOVIES':
		addDir(translation(30621), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/beliebteste.html", 'target': 'TRAILERS'})
		addDir(translation(30622), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/imkino/", 'target': 'TRAILERS'})
		addDir(translation(30623), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/bald/", 'target': 'TRAILERS'})
		addDir(translation(30624), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/neu/", 'target': 'TRAILERS'})
		addDir(translation(30625), icon, {'mode': 'filtrating', 'url': f"{BASE_URL}/trailer/archiv/", 'target': 'ARCHIVES'})
	else:
		addDir(translation(30626), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/serien/kurz/", 'target': 'TRAILERS'})
		addDir(translation(30627), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/serien/meisterwartete/", 'target': 'TRAILERS'})
		addDir(translation(30628), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/trailer/serien/neueste/", 'target': 'TRAILERS'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def movies():
	addDir(translation(30631), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/filme-imkino/vorpremiere/"})
	addDir(translation(30632), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/filme-imkino/kinostart/"})
	addDir(translation(30633), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/filme-imkino/neu/"})
	addDir(translation(30634), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/filme-imkino/besten-filme/user-wertung/"})
	addDir(translation(30635), icon, {'mode': 'selectionWeeks', 'url': f"{BASE_URL}/filme-vorschau/de/"})
	addDir(translation(30636), icon, {'mode': 'filtrating', 'url': f"{BASE_URL}/kritiken/filme-alle/user-wertung/", 'target': 'MOVIES'})
	addDir(translation(30637), icon, {'mode': 'filtrating', 'url': f"{BASE_URL}/kritiken/filme-alle/", 'target': 'MOVIES'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def series():
	addDir(translation(30641), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/top/"})
	addDir(translation(30642), icon, {'mode': 'filtrating', 'url': f"{BASE_URL}/serien/beste/", 'target': 'SERIES'})
	addDir(translation(30643), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/top/populaerste/"})
	addDir(translation(30644), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/kommende-staffeln/meisterwartete/"})
	addDir(translation(30645), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/kommende-staffeln/"})
	addDir(translation(30646), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/kommende-staffeln/demnaechst/"})
	addDir(translation(30647), icon, {'mode': 'listVideos', 'url': f"{BASE_URL}/serien/neue/"})
	addDir(translation(30648), icon, {'mode': 'filtrating', 'url': f"{BASE_URL}/serien-archiv/", 'target': 'SERIES'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def filtrating(url, CATEGORY):
	debug_MS("(navigator.filtrating) -------------------------------------------------- START = filtrating --------------------------------------------------")
	debug_MS(f"(navigator.filtrating) ### URL = {url} ### CATEGORY = {CATEGORY} ###")
	if not 'genre-' in url:
		addDir(translation(30801), icon, {'mode': 'selectionArticles', 'url': url, 'target': CATEGORY, 'extras': 'Nach Genre'})
	if CATEGORY == 'ARCHIVES':
		if not 'sprache-' in url:
			addDir(translation(30802), icon, {'mode': 'selectionArticles', 'url': url, 'target': CATEGORY, 'extras': 'Nach Sprache'})
		if not 'format-' in url:
			addDir(translation(30803), icon, {'mode': 'selectionArticles', 'url': url, 'target': CATEGORY, 'extras': 'Nach Typ'})
	else:
		if not 'jahrzehnt' in url:
			addDir(translation(30804), icon, {'mode': 'selectionArticles', 'url': url, 'target': CATEGORY, 'extras': 'Nach Produktionsjahr'})
		if not 'produktionsland-' in url:
			addDir(translation(30805), icon, {'mode': 'selectionArticles', 'url': url, 'target': CATEGORY, 'extras': 'Nach Land'})
	addDir(translation(30806), icon, {'mode': 'listVideos', 'url': url, 'target': CATEGORY})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionArticles(url, CATEGORY, TYPE):
	debug_MS("(navigator.selectionArticles) -------------------------------------------------- START = selectionArticles --------------------------------------------------")
	debug_MS(f"(navigator.selectionArticles) ### URL = {url} ### CATEGORY = {CATEGORY} ### TYPE = {TYPE} ###")
	content = getUrl(url, 'LOAD')
	result = content[content.find('data-name="'+TYPE+'"')+1:]
	result = result[:result.find('</ul>')]
	part = result.split('class="filter-entity-item"')
	for i in range(1, len(part), 1):
		entry = re.sub(r'</?strong>', '', part[i])
		matchH1 = re.compile(r'''class=["']item-content["'] href=["']([^"']+)["'] title=.+?["']>([^<]+?)</a>''', re.S).findall(entry)
		matchH2 = re.compile(r'''<span class=["']ACr([^"']+) item-content["'] title=.+?["']>([^<]+?)</span>''', re.S).findall(entry)
		LINK = BASE_URL+matchH1[0][0] if matchH1 else BASE_URL+convert64(matchH2[0][0])
		NAME = cleaning(matchH1[0][1]) if matchH1 else cleaning(matchH2[0][1])
		matchNUM = re.compile(r'''<span class=["']light["']>\(([^<]+?)\)</span>''', re.S).findall(entry)
		if matchNUM: NAME += translation(30831).format(str(matchNUM[0].strip()))
		addDir(NAME, icon, {'mode': 'filtrating', 'url': LINK, 'target': CATEGORY})
		debug_MS(f"(navigator.selectionArticles[1]) ##### NAME : {NAME} || LINK : {LINK} #####")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionWeeks(url):
	debug_MS("(navigator.selectionWeeks) -------------------------------------------------- START = selectionWeeks --------------------------------------------------")
	debug_MS(f"(navigator.selectionWeeks) ### URL = {url} ###")
	content = getUrl(url, 'LOAD')
	result = content[content.find('<div class="pagination pagination-select">')+1:]
	result = result[:result.find('<span class="txt">Nächste</span><i class="icon icon-right icon-arrow-right-a">')]
	matchOPT = re.compile(r'''<option value=["']ACr([^"']+)["']([^<]+)</option>''', re.S).findall(result)
	for linkway, title in matchOPT:
		LINK = BASE_URL+convert64(linkway)
		DATES = re.sub(r'filme-vorschau/de/week-|/', '', linkway)
		title = title.replace('>', '')
		NAME = translation(30832).format(cleaning(title.replace('selected', ''))) if 'selected' in title else cleaning(title)
		addDir(NAME, icon, {'mode': 'listVideos', 'url': LINK, 'target': 'PREVIEWS'})
		debug_MS(f"(navigator.selectionWeeks[1]) ##### NAME : {NAME} || DATE : {DATES} #####")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(url, PAGE, POS, CATEGORY):
	debug_MS("(navigator.listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	UNIKAT, counter, SEND = set(), 0, {}
	COMBI_FIRST, COMBI_LINKS, COMBI_SECOND, SEND['videos'] = ([] for _ in range(4))
	NEW_URL = f"{url}?page={PAGE}" if int(PAGE) > 1 else url
	debug_MS(f"(navigator.listVideos) ### URL = {NEW_URL} ### PAGE = {PAGE} ### POSITION = {POS} ### TARGET = {CATEGORY} ###")
	content = getUrl(NEW_URL, 'LOAD')
	if enableBACK and PLACEMENT == '0' and int(PAGE) > 1:
		addDir(translation(30833), f"{artpic}backmain.png", {'mode': 'callingMain'})
	matchPG = re.findall(r'''<nav class=["']pagination(.+?)<div class=["']mdl-rc["']>''', content, re.S)
	if int(POS) == 0 and matchPG:
		PG_ONE = re.compile(r'''<a class=["']button button-md item["'] href=.+?page=[0-9]+["']>([0-9]+)</a></div></nav>''', re.S).findall(matchPG[0])
		PG_TWO = re.compile(r'''<span class=["']ACr.+?button-md item["']>([0-9]+)</span></div></nav>''', re.S).findall(matchPG[0])
		POS = PG_ONE[0] if PG_ONE else PG_TWO[0] if PG_TWO else POS
		debug_MS(f"(navigator.listVideos[1]) NEXTPAGES ### Pages-Maximum : {str(POS)} ###")
	result = content[content.find('<main id="content-layout" class="content-layout cf">')+1:]
	result = result[:result.find('<div class="mdl-rc">')]
	part = result.split('<figure class="thumbnail')
	for i in range(1, len(part), 1):
		entry = re.sub(r'</?strong>', ' ', part[i])
		debug_MS(f"(navigator.listVideos[1]) xxxxx ENTRY-01 : {str(entry)} xxxxx")
		DESC_1 = ""
		DATE_1, RATING_1 = (None for _ in range(2))
		GENRE_1, DIRECTOR_1, WRITER_1, CAST_1 = ([] for _ in range(4))
		matchH1 = re.compile(r'''(?:class=["']meta-title-link["']|class=["']layer-link-holder["']><a) href=["']([^"']+)["'](?: class=["']layer-link["'])?>([^<]+)</a>''', re.S).findall(entry)
		matchH2 = re.compile(r'''class=["']thumbnail-container thumbnail-link["'] href=["']([^"']+?)["'] title=["']([^"']+)["']>''', re.S).findall(entry)
		matchH3 = re.compile(r'''class=["']ACr([^ "']+) thumbnail-container thumbnail-link["'] title=["']([^"']+)["']''', re.S).findall(entry)
		ORLINK_1 = BASE_URL+matchH1[0][0] if matchH1 else BASE_URL+matchH2[0][0] if matchH2 else BASE_URL+convert64(matchH3[0][0])
		WFLINK_1 = ORLINK_1.split('/videos')[0]+'.html' if '/videos' in ORLINK_1 else ORLINK_1.split('/trailer')[0]+'.html' if '/trailer' in ORLINK_1 else ORLINK_1.split('/staffel')[0]+'.html' if '/staffel' in ORLINK_1 else ORLINK_1
		if CATEGORY != 'INTERVIEWS' and WFLINK_1 in UNIKAT:
			continue
		UNIKAT.add(WFLINK_1)
		TITLE_1 = cleaning(matchH1[0][1]) if matchH1 else cleaning(matchH2[0][1]) if matchH2 else cleaning(matchH3[0][1])
		IMAGE_1 = re.compile(r'''(?:class=["']thumbnail-img["'] |data-)src=["'](https?://.+?[a-z0-9]+(?:\.png|\.jpg|\.jpeg|\.gif))["'?]''', re.S|re.I).findall(entry)[0]
		THUMB_1 = enlargeIMG(IMAGE_1)
		agreeDUR = re.compile(r'''class=["']thumbnail-count["']>([^<]+?)</span>''', re.S).findall(entry) # Grab - Duration
		DURATION_1 = get_Time(agreeDUR[0]) if agreeDUR and len(agreeDUR[0]) > 0 else None # 1:55
		agreeVIS = re.compile(r'''class=["']meta-sub light["']>(.+?)</div>''', re.S).findall(entry)
		VISITORS_1 = cleaning(re.sub(r'\<.*?\>', '', agreeVIS[0])) if agreeVIS else None
		counter += 1
		WORKS_1 = True if '<span class="icon icon-play-arrow"></span>' in entry or DURATION_1 is not None else False
		if CATEGORY == 'INTERVIEWS':
			DESC_1, TITLE_1 = TITLE_1, 'FILMSTARTS - Interview'
			DESC_1 += translation(30834).format(str(VISITORS_1)) if VISITORS_1 else ""
		if CATEGORY not in ['ARCHIVES', 'INTERVIEWS', 'TRAILERS']:
			AREA_1 = re.compile(r'''<div class=["']meta-body-item meta-body-info(.+?)</div>''', re.S).findall(entry) # Grab - Genres
			if '<span class="spacer">' in entry:
				AREA_1 = re.compile(r'''<span class=["']spacer["']>(.+?)<div class=["']meta-body-item(?: meta-body-direction)?''', re.S).findall(entry)
			agreeGEN = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(AREA_1[0]) if AREA_1 else []
			GENRE_1 = ' / '.join(sorted([cleaning(genpart) for genpart in agreeGEN])) if agreeGEN else [] # Drama, Familie, Komödie
			AREA_2 = re.compile(r'''<span class=["']light["']>Regie(.+?)</div>''', re.S).findall(entry) # Grab - Directors
			agreeDIR = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_2[0]) if AREA_2 else []
			DIRECTOR_1 = ', '.join([cleaning(dirpart) for dirpart in agreeDIR]) if agreeDIR else [] # Steven Seagal
			AREA_3 = re.compile(r'''<span class=["']light["']>(?:Drehbuch|Creator)(.+?)</div>''', re.S).findall(entry) # Grab - Writers
			agreeCREA = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_3[0]) if AREA_3 else []
			WRITER_1 = ', '.join([cleaning(creapart) for creapart in agreeCREA]) if agreeCREA else [] # Ed Horowitz, Robin U. Russin
			AREA_4 = re.compile(r'''<span class=["']light["']>Besetzung(.+?)</div>''', re.S).findall(entry) # Grab - Casts
			agreeACT = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(AREA_4[0]) if AREA_4 else []
			if agreeACT and len(agreeACT) > 0: # Fran Monegan, Gabriel L. Muktoyuk, Helen Hakkila
				for index, person in enumerate(agreeACT, 1):
					actor = {'name': cleaning(re.sub(r'\<.*?>', '', person)), 'role': '', 'order': index, 'thumb': ''}
					if actor['name'] not in ['' , None]:
						if KODI_ov20:
							CAST_1.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], actor['thumb']))
						else: CAST_1.append(actor)
			agreePLOT = re.compile(r'''<div class=["']content-txt(?: )?["']>(.+?)</div>''', re.S).findall(entry) # Grab - Plot
			DESC_1 = cleaning(re.sub(r'\<.*?\>', '', agreePLOT[0])) if agreePLOT else ""
			agreeDAT = re.compile(r'''<span class=["'](?:ACr.*?)?date(?: )?["']>(.+?)<span class=''', re.S).findall(entry) # Grab - Date
			if '/serien' in ORLINK_1 or not agreeDAT:
				agreeDAT = re.compile(r'''<div class=["']meta-body-item meta-body-info["']>(.+?)<span class=["']spacer["']>''', re.S).findall(entry) # Grab - Date
			DATE_1 = cleaning(re.sub(r'\<.*?>', '', agreeDAT[0].replace('\n', '').replace(' - ', ' ~ '))) if agreeDAT and len(agreeDAT[0]) > 0 else None # 20. Februar 2024 auf Amazon
			try:
				AREA_5 = (entry[entry.find('User-Wertung')+1:] or entry[entry.find('Pressekritiken')+1:]) # Grab - Rating
				RATING_1 = re.compile(r'''class=["']stareval-note["']>([^<]+?)</span>''', re.S).findall(AREA_5)[0].strip().replace(',', '.') # 2,5
			except: pass
			COMBI_FIRST.append([int(counter), ORLINK_1, WFLINK_1, url, TITLE_1, THUMB_1, GENRE_1, DIRECTOR_1, WRITER_1, CAST_1, DESC_1, DATE_1, RATING_1, DURATION_1, WORKS_1])
			COMBI_LINKS.append([int(counter), CATEGORY, ORLINK_1, WFLINK_1])
		else:
			COMBI_FIRST.append([int(counter), ORLINK_1, WFLINK_1, url, TITLE_1, THUMB_1, GENRE_1, DIRECTOR_1, WRITER_1, CAST_1, DESC_1, DATE_1, RATING_1, DURATION_1, WORKS_1])
			COMBI_LINKS.append([int(counter), CATEGORY, ORLINK_1, WFLINK_1])
	if COMBI_FIRST and CATEGORY != 'INTERVIEWS': # Für Interviews kein Aufruf der 'COMBI_SECOND'
		COMBI_SECOND = listSubstances(COMBI_LINKS)
	if COMBI_FIRST or COMBI_SECOND: # Zähler NULL ist immer die Nummerierungder Listen 1+2
		RESULT = [a + b for a in COMBI_FIRST for b in COMBI_SECOND if a[0] == b[0]] # Zusammenführung von Liste1 und Liste2 - wenn die Nummer an erster Stelle(0) überein stimmt !!!
		if CATEGORY == 'INTERVIEWS':
			RESULT = COMBI_FIRST # Für Interviews keine 'COMBI_SECOND'
		for da in sorted(RESULT, key=lambda k: int(k[0]), reverse=False): # 0-14 = Liste1 || 15-34 = Liste2
			debug_MS("* * * * * * * * * * * * * * * * * * * * * * *")
			debug_MS(f"(navigator.listVideos[3]) ### Anzahl = {str(len(da))} || Eintrag : {str(da)} ###")
			Note_1, Note_2, Note_3 = ("" for _ in range(3))
			if len(da) > 15: ### Liste2 beginnt mit Nummer:15 ###
				Number1, oLink1, wLink1, uLink1, Title1, Thumb1, Genre1, Director1, Writer1, Cast1, Desc1, Date1, Rating1, Dur1, Works1 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11], da[12], da[13], da[14]
				Number2, oExtra2, oLink2, oLink3, Title2, Thumb2, Genre2, original, Director2, Writer2, Cast2, country, Mpaa2, Desc2, seasons, Date2, Rating2, Dur2, Works2, TEASER = da[15], da[16], da[17], da[18], da[19], da[20], da[21], da[22], da[23], da[24], da[25], da[26], da[27], da[28], da[29], da[30], da[31], da[32], da[33], da[34]
			else:
				Number1, oLink1, wLink1, uLink1, Title1, Thumb1, Genre1, Director1, Writer1, Cast1, Desc1, Date1, Rating1, Dur1, Works1 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11], da[12], da[13], da[14]
				Number2, oExtra2, oLink2, oLink3, Title2, Thumb2, Genre2, original, Director2, Writer2, Cast2, country, Mpaa2, Desc2, seasons, Date2, Rating2, Dur2, Works2, TEASER = 0, 'standard', None, None, None, None, None, None, None, None, [], None, None, "", None, None, None, 0, False, None
			title = Title2 if Title2 and CATEGORY != 'ARCHIVES' else Title1
			duration = Dur2 if Dur2 and CATEGORY != 'ARCHIVES' else Dur1 if Dur1 else None
			image = Thumb2 if Thumb2 and CATEGORY != 'ARCHIVES' else Thumb1 if Thumb1 else None
			genre = Genre2 if Genre2 else Genre1 if Genre1 else None
			director = Director2 if Director2 else Director1 if Director1 else None
			writer = Writer2 if Writer2 else Writer1 if Writer1 else None
			cast = Cast2 if Cast2 else Cast1
			STARTING = Date2 if Date2 else Date1
			rating = Rating2 if Rating2 else Rating1
			mpaa = translation(30835) if Mpaa2 and '0' in str(Mpaa2) else Mpaa2
			works = True if Works2 is True or Works1 is True else False
			transmit = TEASER if TEASER else oLink1
			if works is True:
				name = title
				uvz = build_mass({'mode': 'playCODE', 'IDENTiTY': transmit})
			else:
				name = translation(30836).format(title)
				uvz = build_mass({'mode': 'blankFUNC', 'url': 'NO VIDEO'})
			if seasons:
				Note_1 = translation(30837).format(seasons)
			if Date2 or Date1:
				BEGINNING = Date2.replace('er Starttermin', '') if Date2 else Date1.replace('er Starttermin', '')
				Note_2 = translation(30838).format(BEGINNING)
			if seasons and Date1 is None and Date2 is None: Note_2 = '[CR]'
			Note_3 = Desc2 if len(Desc2) > len(Desc1) else Desc1
			plot = Note_1+Note_2+Note_3
			debug_MS(f"(navigator.listVideos[3]) ##### NAME : {name} || LINK : {str(transmit)} || DATE : {str(STARTING)} #####")
			debug_MS(f"(navigator.listVideos[3]) ##### GENRE : {str(genre)} || DIRECTOR : {str(director)} || WRITER : {str(writer)} || RATING : {str(rating)} #####")
			debug_MS(f"(navigator.listVideos[3]) ##### TRAILER : {str(works)} || DURATION : {str(duration)} || THUMB : {str(image)} #####")
			LSM = xbmcgui.ListItem(name)
			if plot in ['', 'None', None]: plot = "..."
			if KODI_ov20:
				vinfo = LSM.getVideoInfoTag()
				vinfo.setTitle(name)
				if original: vinfo.setOriginalTitle(original)
				vinfo.setPlot(plot)
				if str(duration).isdigit(): vinfo.setDuration(int(duration))
				if country: vinfo.setCountries([country])
				if genre and len(genre) > 3: vinfo.setGenres([genre])
				if director: vinfo.setDirectors([director])
				if writer: vinfo.setWriters([writer])
				if isinstance(cast, (list, tuple)): vinfo.setCast(cast)
				if rating and str(rating.replace('.', '')).isdigit(): vinfo.setRating(float(rating), 0, 'userrating', True) # vinfo.setRating(4.6, 8940, "imdb", True) since NEXUS and UP
				if mpaa: vinfo.setMpaa(mpaa)
				vinfo.setMediaType('movie')
			else:
				vinfo = {}
				if isinstance(cast, (list, tuple)): LSM.setCast(cast)
				vinfo['Title'] = name
				if original: vinfo['OriginalTitle'] = original
				vinfo['Plot'] = plot
				if str(duration).isdigit(): vinfo['Duration'] = duration
				if country: vinfo['Country'] = country
				if genre and len(genre) > 3: vinfo['Genre'] = genre
				if director: vinfo['Director'] = director
				if writer: vinfo['Writer'] = writer
				if rating and str(rating.replace('.', '')).isdigit(): LSM.setRating('userrating', float(rating), 0, True) # LSM.setRating("imdb", 4.6, 8940, True) below NEXUS (MATRIX)
				if mpaa: vinfo['Mpaa'] = mpaa
				vinfo['Mediatype'] = 'movie'
				LSM.setInfo(type='Video', infoLabels=vinfo)
			LSM.setArt({'icon': icon, 'thumb': image, 'poster': image})
			if useThumbAsFanart:
				LSM.setArt({'fanart': defaultFanart})
			entries = []
			if enableBACK and PLACEMENT == '1':
				entries.append([translation(30650), 'RunPlugin({})'.format(build_mass({'mode': 'callingMain'}))])
			if works is True:
				LSM.setProperty('IsPlayable', 'true')
				LSM.setContentLookup(False)
				entries.append([translation(30654), 'Action(Queue)'])
			LSM.addContextMenuItems(entries)
			SEND['videos'].append({'filter': transmit, 'name': name, 'photo': image, 'genre': genre, 'plot': plot})
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LSM)
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
	if counter == 0:
		return dialog.notification(translation(30524), translation(30525), icon, 10000)
	if BEFORE_AND_AFTER and CATEGORY == 'PREVIEWS':
		try:
			LEFT = convert64(re.compile(r'''<span class=["']ACr([^ "']+) button button-md button-primary-full button-left["']>.*?span class=["']txt["']>Vorherige</span>''', re.S).findall(result)[0])
			RIGHT = convert64(re.compile(r'''<span class=["']ACr([^ "']+) button button-md button-primary-full button-right["']>.*?span class=["']txt["']>Nächste</span>''', re.S).findall(result)[0])
			BeforeDAY, AfterDAY = re.sub(r'filme-vorschau/de/week-|/', '', LEFT), re.sub(r'filme-vorschau/de/week-|/', '', RIGHT)
			before, after = datetime(*(time.strptime(BeforeDAY, '%Y-%m-%d')[0:6])), datetime(*(time.strptime(AfterDAY, '%Y-%m-%d')[0:6]))
			bxORG, axORG = before.strftime('%Y-%m-%d'), after.strftime('%Y-%m-%d')
			bxNEW, axNEW = before.strftime('%d.%m.%Y'), after.strftime('%d.%m.%Y')
			addDir(translation(30839).format(str(axNEW)), icon, {'mode': 'listVideos', 'url': BASE_URL+RIGHT, 'target': CATEGORY})
			addDir(translation(30840).format(str(bxNEW)), icon, {'mode': 'listVideos', 'url': BASE_URL+LEFT, 'target': CATEGORY})
		except: pass
	if int(POS) > int(PAGE) and CATEGORY != 'PREVIEWS':
		debug_MS(f"(navigator.listVideos[4]) NEXTPAGES ### Now show NextPage ... No.{str(int(PAGE)+1)} ... ###")
		addDir(translation(30841).format(int(PAGE)+1), f"{artpic}nextpage.png", {'mode': 'listVideos', 'url': url, 'page': int(PAGE)+1, 'position': int(POS), 'target': CATEGORY})
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=True, cacheToDisc=False)

def listSubstances(MURLS):
	debug_MS("(navigator.listSubstances) -------------------------------------------------- START = listSubstances --------------------------------------------------")
	COMBI_DETAILS, COMBI_THIRD = ([] for _ in range(2))
	COMBI_DETAILS = getMultiData(MURLS)
	if COMBI_DETAILS:
		#log("++++++++++++++++++++++++")
		#log(f"(navigator.llistSubstances[2]) XXXXX CONTENT-02 : {str(COMBI_DETAILS)} XXXXX")
		#log("++++++++++++++++++++++++")
		for number, CATEGORY_2, ORLINK_2, WFLINK_2, elem in COMBI_DETAILS:
			if elem is not None:
				RATING_2, (TRAILER_2, WORKS_2) = None, (False for _ in range(2))
				GENRE_2, DIRECTOR_2, WRITER_2, CAST_2, COUNTRY_2 = ([] for _ in range(5))
				details = re.findall(r'''<main id=["']content-layout["'] class=["'](?:row )?content-layout entity (?:movie|series) cf(.*?)<section class=["']js-outbrain section(?: )?["']>''', elem, re.S)
				for item in details:
					item = re.sub(r'</?strong>', ' ', item)
					debug_MS(f"(navigator.listSubstances[2]) xxxxx ITEM-02 : {str(item)} xxxxx")
					SECTOR_1 = re.compile(r'''class=["']card entity-card entity-card-list cf(.+?)</figure>''', re.S).findall(item) # Grab - Title + Link + Photo
					matchL1 = re.compile(r'''class=["']thumbnail-container thumbnail-link["'] href=["']([^"']+?)["'] title=["'](.+?)["']>''', re.S).findall(SECTOR_1[0]) if SECTOR_1 else None # Grab - Link
					matchL2 = re.compile(r'''class=["']ACr([^ "']+) thumbnail-container thumbnail-link["'] title=["'](.+?)["']>''', re.S).findall(SECTOR_1[0]) if SECTOR_1 else None # Grab - Link
					ORLINK_3 = BASE_URL+matchL1[0][0] if matchL1 else BASE_URL+convert64(matchL2[0][0]) if matchL2 else None
					NAME_2 = cleaning(matchL1[0][1]) if matchL1 else cleaning(matchL2[0][1]) if matchL2 else None
					IMAGE_2 = re.compile(r'''class=["']thumbnail-img["'] (?:.*?data-)?src=["'](https?://.+?[a-z0-9]+(?:\.png|\.jpg|\.jpeg|\.gif))["'?]''', re.S|re.I).findall(SECTOR_1[0]) if SECTOR_1 else None
					THUMB_2 = enlargeIMG(IMAGE_2[0]) if IMAGE_2 and not 'empty/' in IMAGE_2[0] else None
					SECTOR_2 = re.compile(r'''<div class=["']meta-body-item meta-body-info(.+?)</div>''', re.S).findall(item) # Grab - Genres
					if '<span class="spacer">' in item:
						SECTOR_2 = re.compile(r'''<span class=["']spacer["']>(.+?)<div class=["']meta-body-item(?: meta-body-direction)?''', re.S).findall(item) # Grab - Genres
					matchGEN = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(SECTOR_2[0]) if SECTOR_2 else []
					GENRE_2 = ' / '.join(sorted([cleaning(genpart) for genpart in matchGEN])) if matchGEN else [] # Drama, Familie, Komödie
					matchORG = re.compile(r'''<span class=["']light["']>Originaltitel:(.+?)</div>''', re.S).findall(item) # Grab - Originaltitle
					ORIGINAL_2 = cleaning(re.sub(r'\<.*?>', '', matchORG[0])) if matchORG else None # World on Fire
					SECTOR_3 = re.compile(r'''<span class=["']light["']>Regie(.+?)</div>''', re.S).findall(item) # Grab - Directors
					matchDIR = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_3[0]) if SECTOR_3 else []
					DIRECTOR_2 = ', '.join([cleaning(dirpart) for dirpart in matchDIR]) if matchDIR else [] # Steven Seagal
					SECTOR_4 = re.compile(r'''<span class=["']light["']>(?:Drehbuch|Creator)(.+?)</div>''', re.S).findall(item) # Grab - Writers
					matchCREA = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_4[0]) if SECTOR_4 else []
					WRITER_2 = ', '.join([cleaning(creapart) for creapart in matchCREA]) if matchCREA else [] # Ed Horowitz, Robin U. Russin
					SECTOR_5 = re.compile(r'''<span class=["']light["']>Besetzung(.+?)</div>''', re.S).findall(item) # Grab - Casts
					matchACT = re.compile(r'''(?:<span class=["']ACr|href=["']/personen).*?["']>(.+?)(?:</span>|</a>)''', re.S).findall(SECTOR_5[0]) if SECTOR_5 else []
					if matchACT and len(matchACT) > 0: # Fran Monegan, Gabriel L. Muktoyuk, Helen Hakkila
						for index, person in enumerate(matchACT, 1):
							actor = {'name': cleaning(re.sub(r'\<.*?>', '', person)), 'role': '', 'order': index, 'thumb': ''}
							if actor['name'] not in ['' , None]:
								if KODI_ov20:
									CAST_2.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], actor['thumb']))
								else: CAST_2.append(actor)
					SECTOR_6 = re.compile(r'''<span class=["']light["']>Produktions(?:land|länder)(.+?)</div>''', re.S).findall(item) # Grab - Countries
					matchCOU = re.compile(r'''<span class=["']ACr.*?["']>(.+?)</span>''', re.S).findall(SECTOR_6[0]) if SECTOR_6 else []
					COUNTRY_2 = ', '.join(sorted([cleaning(coupart) for coupart in matchCOU])) if matchCOU else [] # Deutschland
					matchAGE = re.compile(r'''<span class=["']certificate-text(?: )?["']>(.+?)</span>''', re.S).findall(item) # Grab - Mpaa
					MPAA_2 = cleaning(matchAGE[0]) if matchAGE else None # FSK ab 18
					matchPLOT = re.compile(r'''<div class=["']content-txt(?: )?["']>(.+?)</div>''', re.S).findall(item) # Grab - Plot
					DESC_2 = cleaning(re.sub(r'\<.*?\>', '', matchPLOT[0])) if matchPLOT else ""
					SECTOR_7 = re.compile(r'''class=["']stats-numbers-row stats-numbers-seriespage(.+?)class=["']end-section-link-container''', re.S).findall(item) # Grab - Seasons + Episodes
					matchSEA = re.compile(r'''<div class=["']stats-item(?: )?["']>(.+?)</div>''', re.S).findall(SECTOR_7[0]) if SECTOR_7 else []
					SEASON_2 = ' • '.join([cleaning(seapart) for seapart in matchSEA]) if matchSEA else [] # 20 Staffeln • 420 Episoden
					matchDAT = re.compile(r'''<span class=["'](?:ACr.*?)?date(?: )?["']>(.+?)<span class=''', re.S).findall(item) # Grab - Date
					if ORLINK_3 and ('/serien' in ORLINK_3 or not matchDAT):
						matchDAT = re.compile(r'''<div class=["']meta-body-item meta-body-info["']>(.+?)<span class=["']spacer["']>''', re.S).findall(item) # Grab - Date
					DATE_2 = cleaning(re.sub(r'\<.*?>', '', matchDAT[0].replace('\n', '').replace(' - ', ' ~ '))) if matchDAT and len(matchDAT[0]) > 0 else None # 20. Februar 2024 auf Amazon
					try:
						SECTOR_8 = (item[item.find('User-Wertung')+1:] or item[item.find('Pressekritiken')+1:]) # Grab - Rating
						RATING_2 = re.compile(r'''class=["']stareval-note["']>([^<]+?)</span>''', re.S).findall(SECTOR_8)[0].strip().replace(',', '.') # 2,5
					except: pass
					SECTOR_9 = re.compile(r'''class=["']card video-card video-card-col(.+?)</section>''', re.S).findall(item) # Grab - Videos
					matchTR1 = re.compile(r'''<span class=["']ACr([^ "']+?) meta-title-link["']>([^<]+?)</span>''', re.S).findall(SECTOR_9[0]) if SECTOR_9 else [] # <span class="ACrL2tACryaXRpa2VuLzMwODMxNi90cmFpbGVyLzE5NTk0NjgxLmh0bWw= meta-title-link">
					matchTR2 = re.compile(r'''class=["']meta-title-link["'] href=["']([^"']+?)["']>([^<]+?)</a>''', re.S).findall(SECTOR_9[0]) if SECTOR_9 else [] # <a class="meta-title-link" href="/kritiken/308316/trailer/19594681.html">
					if CATEGORY_2 != 'ARCHIVES':
						TRAILER_2 = BASE_URL+convert64(matchTR1[0][0]) if matchTR1 else BASE_URL+matchTR2[0][0] if matchTR2 else False
					NEW_TITLE = cleaning(matchTR1[0][1]) if matchTR1 else cleaning(matchTR2[0][1]) if matchTR2 else NAME_2
					TITLE_2 = NAME_2+' - '+NEW_TITLE if not NAME_2 in NEW_TITLE else NEW_TITLE
					WORKS_2 = True if TRAILER_2 and ('trailer' in TRAILER_2 or 'teaser' in TRAILER_2 or 'videos' in TRAILER_2) else False
					matchDUR = re.compile(r'''class=["']thumbnail-count["']>([^<]+?)</span>''', re.S).findall(SECTOR_9[0]) if SECTOR_9 else [] # Grab - Duration
					DURATION_2 = get_Time(matchDUR[0]) if matchDUR and len(matchDUR[0]) > 0 else None # 1:55
					COMBI_THIRD.append([int(number), CATEGORY_2, ORLINK_2, ORLINK_3, TITLE_2, THUMB_2, GENRE_2, ORIGINAL_2, DIRECTOR_2, WRITER_2, CAST_2, COUNTRY_2, MPAA_2, DESC_2, SEASON_2, DATE_2, RATING_2, DURATION_2, WORKS_2, TRAILER_2])
	return COMBI_THIRD

def playCODE(SOURCE):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS(f"(navigator.playCODE) ### TRAILER_SOURCE : {SOURCE} ###")
	MEDIAS, (TRAILER_LINK, FINAL_URL) = [], (False for _ in range(2))
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for record in ARRIVE['videos']:
			if record['filter'] != '00' and record['filter'] == SOURCE:
				TRAILER_LINK = record['filter']
				CLEAR_TITLE = record['name']
				PHOTO = record['photo']
				GENRE = record['genre']
				PLOT = record['plot']
				debug_MS(f"(navigator.playCODE[1]) ### WORKFILE-Line : {str(record)} ###")
	if TRAILER_LINK:
		result = getUrl(TRAILER_LINK, method='LOAD', REF=f"{BASE_URL}/")
		MP4_QUALITIES = ['high', 'standard', 'medium', 'low'] # high=_hd_013.mp4 // low=_l_013.mp4 // medium=_m_013.mp4 // standard=_sd_013.mp4
		THIRD = re.compile(r'''(?:class=["']player  js-player["']|class=["']player player-auto-play js-player["']|<div id=["']btn-export-player["'].*?) data-model=["'](.+?),&quot;disablePostroll&quot;''', re.S).findall(result)
		STREAMS = THIRD[0].replace('&quot;', '"')+'}' if THIRD else None
		debug_MS(f"(navigator.playCODE[2]) ##### Extraction of Stream-Links : {str(STREAMS)} #####")
		if STREAMS:
			DATA = json.loads(STREAMS)
			for item in DATA.get('videos', []):
				vidQualities = item.get('sources', '')
				for found in MP4_QUALITIES:
					for quality in vidQualities:
						if quality == found:
							MEDIAS.append({'url': vidQualities[quality], 'quality': quality, 'mimeType': 'video/mp4'})
	if MEDIAS:
		FINAL_URL = VideoBEST(MEDIAS[0]['url'])
		FINAL_URL = f"https:{FINAL_URL.replace(' ', '%20')}" if FINAL_URL[:4] != 'http' else FINAL_URL.replace(' ', '%20')
		LSM = xbmcgui.ListItem(CLEAR_TITLE, path=FINAL_URL)
		log(f"(navigator.playCODE) StreamURL : {FINAL_URL}")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
	else:
		failing(f"(navigator.playCODE[3]) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####\n ##### URL : {SOURCE} #####")
		return dialog.notification(translation(30521).format('PLAY'), translation(30526), icon, 8000)

def VideoBEST(highest):
	standards = [highest, '', ''] # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	standards[1] = standards[0].replace('_l_', '_sd_').replace('_m_', '_sd_')
	standards[2] = standards[1].replace('_sd_', '_hd_')
	if standards[0] not in [standards[1], standards[2]]:
		for xy, element in enumerate(reversed(standards), 1):
			try:
				code = urlopen(element, timeout=6).getcode()
				if code in [200, 201, 202]:
					return element
			except: pass
	return highest

def addDir(name, image, params={}, plot='...', folder=True):
	u = build_mass(params)
	liz = xbmcgui.ListItem(name)
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setPlot(plot)
	else:
		liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)
