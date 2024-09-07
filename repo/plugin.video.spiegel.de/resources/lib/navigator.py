# -*- coding: utf-8 -*-

from .common import *
from .external.scrapetube import *


if not xbmcvfs.exists(os.path.join(dataPath, 'settings.xml')):
	xbmcvfs.mkdirs(dataPath)
	xbmc.executebuiltin(f"Addon.OpenSettings({addon_id})")

def mainMenu():
	addDir(translation(30601), f"{artpic}uebersicht.png", {'mode': 'listArticles', 'url': f"{BASE_URL}video/", 'limit': '2'})
	addDir(translation(30602), f"{artpic}thema.png", {'mode': 'listSpiegelTV'})
	addDir(translation(30603), f"{artpic}panorama.png", {'mode': 'listArticles', 'url': f"{BASE_URL}panorama/", 'limit': '20'})
	addDir(translation(30604), f"{artpic}ausland.png", {'mode': 'listArticles', 'url': f"{BASE_URL}ausland/", 'limit': '20'})
	addDir(translation(30605), f"{artpic}ukraine.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/ukraine_konflikt/", 'limit': '5'})
	addDir(translation(30606), f"{artpic}deutschland.png", {'mode': 'listArticles', 'url': f"{BASE_URL}politik/deutschland/", 'limit': '10'})
	addDir(translation(30607), f"{artpic}talk.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spitzengespraech-der-talk-mit-markus-feldenkirchen/", 'limit': '-3'})
	addDir(translation(30608), f"{artpic}bestseller.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-bestseller-mehr-lesen-mit-elke-heidenreich/"})
	addDir(translation(30609), f"{artpic}autotests.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/auto-tests-im-video/", 'limit': '-3'})
	if enableYOUTUBE:
		addDir(translation(30610), f"{artpic}youtube.png", {'mode': 'listPlaylists'})
	if enableADJUSTMENT:
		addDir(translation(30611), f"{artpic}settings.png", {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30612), f"{artpic}settings.png", {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSpiegelTV():
	addDir(translation(30621), f"{genpic}magazin.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'limit': '-4'})
	addDir(translation(30622), f"{genpic}reportage.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_reportage'})
	addDir(translation(30623), f"{genpic}arte.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_für_arte_re:'})
	addDir(translation(30624), f"{genpic}klassiker.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'klassiker'})
	addDir(translation(30625), f"{genpic}crime.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'spiegel_tv_true_crime'})
	addDir(translation(30626), f"{genpic}verhoer.png", {'mode': 'listArticles', 'url': f"{BASE_URL}thema/spiegel-tv/", 'extras': 'im_verhör'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listArticles(url, plusLIMIT, EXTRA):
	debug_MS("(navigator.listArticles) -------------------------------------------------- START = listArticles --------------------------------------------------")
	debug_MS(f"(navigator.listArticles) ### URL = {url} ### PAGINATION = {str(PAGINATION)} ### plusLIMIT = {plusLIMIT} ### EXTRA = {EXTRA} ###")
	COMBI_PAGES, COMBI_ARTICLES, COMBI_LINKS, COMBI_MEDIA, COMBI_FIRST, COMBI_SECOND, COMBI_THIRD, COMBI_FOURTH = ([] for _ in range(8))
	RESULT_ONE, RESULT_TWO = (None for _ in range(2))
	counter = 0
	UNIKAT = set()
	AMOUNT_PAGES = 2 if EXTRA != 'DEFAULT' else PAGINATION+int(plusLIMIT)
	for ii in range(1, AMOUNT_PAGES, 1):
		WLINK_1 = f"{url}p{str(ii)}/" if int(ii) > 1 else url
		debug_MS(f"(navigator.listArticles[1]]) THEME-PAGES XXX POS = {str(ii)} || URL = {WLINK_1} XXX")
		COMBI_PAGES.append([int(ii), 'THEME', WLINK_1, WLINK_1])
	if COMBI_PAGES:
		COMBI_ARTICLES = getMultiData(COMBI_PAGES)
		if COMBI_ARTICLES:
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listArticles[2]) XXXXX COMBI_ARTICLES-02 : {str(COMBI_ARTICLES)} XXXXX")
			#log("++++++++++++++++++++++++")
			debug_MS("------------------------------------------------")
			for num, THEME_2, WLINK_2, DDURL_2, item in sorted(COMBI_ARTICLES, key=lambda k: int(k[0]), reverse=False):
				if item is not None:
					results = []
					if EXTRA != 'DEFAULT':
						results += re.findall(r'<section class="relative flex flex-wrap w-full" data-size="full" (?:data-last="true" )?data-area="block>topic:{}"(.+?)(?:<section class="relative flex flex-wrap w-full"|data-area="article-teaser-list")'.format(EXTRA), item, re.S)
					else:
						results += re.findall(r'<section class="relative flex flex-wrap w-full" data-size="full" data-first="true" data-area="block>topic(.+?)<section class="relative flex flex-wrap w-full"', item, re.S)
						results += re.findall(r'data-area="article-teaser-list"(.+?)data-area="pagination-bar"', item, re.S)
					for chtml in results:
						articles = re.findall(r'data-block-el="articleTeaser"(.+?)</article>', chtml, re.S)
						for entry in articles:
							entry = entry.replace('&#34;', '"')
							DESC_1, PLAY_1 = ("" for _ in range(2))
							markID_1 = '00'
							NAV_1, THUMB_1, TAGLINE_1, META_1, AIRED_1, JSURL_1 = (None for _ in range(6))
							debug_MS(f"(navigator.listArticles[2]) ### ENTRY-02 : {str(entry)} ###")
							NAME = re.compile(r'<article aria-label="(.+?)" (?:data-|class=)', re.S).findall(entry)[0]
							TITLE_1 = cleaning(NAME)
							STREAM = re.compile('<a href="([^"]+?)" target=', re.S).findall(entry)
							if STREAM: NAV_1 = STREAM[0]
							if NAV_1 is None or NAV_1 in UNIKAT:
								continue
							UNIKAT.add(NAV_1)
							# <img data-image-el="img" class="block lazyload h-full mx-auto" src= || <img data-video-el="poster" class="block lazyload h-full mx-auto" src=
							IMG = re.compile('<img data-(?:image|video)-el=".*?src="(https://cdn.prod.www.spiegel.de/images[^"]+?)"', re.S).findall(entry)
							THUMB_1 = IMG[-1].replace('_w288_r1.778_', '_w1200_r1.778_').replace('_w300_r1.778_', '_w1200_r1.778_').replace('_w488_r1.778_', '_w1200_r1.778_') if IMG else None
							if THUMB_1 and '_fd' in THUMB_1:
								THUMB_1 = THUMB_1.split('_fd')[0]+'.jpg'
							# <span class="mb-4 block text-primary-base dark:text-dm-primary-base focus:text-primary-darker hover:text-primary-dark font-sansUI font-bold text-base" data-target-teaser-el="topMark">
							TAG_1 = re.compile(r'data-target-teaser-el="topMark">([^<]+?)</', re.S).findall(entry)
							TAGLINE_1 = cleaning(TAG_1[0]).replace('\n',' ').replace('\t',' ') if TAG_1 else None # Lauterbach und das Scholz-Team
							# <span class="font-sansUI font-normal text-s text-shade-dark dark:text-shade-light" data-target-teaser-el="meta">
							STORY_1 = re.compile(r'data-target-teaser-el="meta">([^<]+?)</', re.S).findall(entry) # Ein Video von Janita Hämäläinen
							STORY_2 = re.compile(r'<span data-auxiliary>(.+?Uhr)</', re.S).findall(entry) # 9. September 2023, 13.37 Uhr
							if STORY_1 and not 'spitzengespraech' in WLINK_2:
								META_1 = cleaning(re.sub(r'\<.*?\>', '', STORY_1[0]))
							if STORY_2 and ' Uhr' in STORY_2[0]:
								try: 
									broadcast = cleaning(STORY_2[0])
									for dt in (('Januar', 'Jan'), ('Februar', 'Feb'), ('März', 'Mar'), ('April', 'Apr'), ('Mai', 'May'), ('Juni', 'Jun'), ('Juli', 'Jul'),
										 ('August', 'Aug'), ('September', 'Sep'), ('Oktober', 'Oct'),('November', 'Nov'), ('Dezember', 'Dec')): broadcast = broadcast.replace(*dt)
									converted = datetime(*(time.strptime(broadcast, '%d. %b %Y, %H.%M Uhr')[0:6])) # 9. September 2023, 13.37 Uhr
									AIRED_1 = converted.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('.', '•', ':')
								except: pass
							# <span class="font-serifUI font-normal text-base leading-loose mr-6" data-target-teaser-el="text">
							STORY_3 = re.compile(r'data-target-teaser-el="text">(.+?)</', re.S).findall(entry) # Beschreibung long
							if STORY_3: DESC_1 = cleaning(re.sub(r'\<.*?\>', '', STORY_3[0]))
							# </svg>\n</span>\n<span class="text-white dark:text-shade-lightest font-sansUI text-s font-bold">27:09</span>\n</span> || </svg>\n</span>\n<span>7 Min</span>\n</span>
							DUR_1 = re.compile('</svg>\s*</span>\s*<spa.+?>([^<]+?)</span>\s*</span>', re.S).findall(entry)
							DURATION_1 = get_Seconds(DUR_1[0].strip()) if DUR_1 else 0
							if re.search(r'data-contains-flags="Spplus-paid"', entry): continue # SpiegelPlus-Beitrag nur mit ABO abrufbar
							elif re.search(r'<span data-icon-auxiliary="Video"', entry):
								JWID_1 = re.compile('data-component="Video" data-settings=.*?,"(?:jwplayerMedia|media)Id":"(.+?)",', re.S).findall(entry)
								JSURL_1 = 'https://vcdn01.spiegel.de/v2/media/{}?poster_width=1280&sources=hls,dash,mp4'.format(JWID_1[0]) if JWID_1 else None
								PLAY_1, markID_1 = 'VIDEO', JWID_1[0] if JWID_1 else '00'
							elif re.search(r'<span data-icon-auxiliary="Audio"', entry):
								if not enableAUDIO: continue # Audioeinträge ausblenden wenn Audio in den Settings ausgeschaltet ist 
								PLAY_1, markID_1 = 'AUDIO', '00'
							else: continue # KEIN Playsymbol (Audio/Video) im THUMB gefunden !!!
							counter += 1
							COMBI_FIRST.append([int(counter), PLAY_1, markID_1, TITLE_1, THUMB_1, NAV_1, META_1, AIRED_1, DESC_1, DURATION_1, TAGLINE_1])
							if JSURL_1 is None and NAV_1:
								COMBI_LINKS.append([int(counter), PLAY_1, NAV_1, NAV_1])
							elif JSURL_1 and NAV_1:
								COMBI_MEDIA.append([int(counter), PLAY_1, NAV_1, JSURL_1])
	if COMBI_FIRST:
		COMBI_SECOND = listSubstances(COMBI_LINKS)
		RESULT_ONE = [a + b for a in COMBI_FIRST for b in COMBI_SECOND if a[5] == b[2]] # Zusammenführung von Liste1 und Liste2 - wenn der LINK überein stimmt !!!
		RESULT_ONE += [c for c in COMBI_FIRST if all(d[2] != c[5] for d in COMBI_SECOND)] # Der übriggebliebene Rest von Liste1 - wenn der LINK nicht in der Liste2 vorkommt !!!
	if COMBI_SECOND or COMBI_MEDIA:
		COMBI_THIRD = getMultiData(COMBI_SECOND+COMBI_MEDIA, WAY='JS')
		if COMBI_THIRD:
			DATA_TWO = json.loads(COMBI_THIRD)
			#log("++++++++++++++++++++++++")
			#log(f"(navigator.listArticles[4]) XXXXX DATA_TWO-04 : {str(DATA_TWO)} XXXXX")
			#log("++++++++++++++++++++++++")
			for elem in DATA_TWO:
				if elem is not None and (('playlist' in elem and elem.get('playlist', [])[0]) or (elem.get('Slug', ''))):
					THUMB_2, AIRED_2, BEGINS_2 = (None for _ in range(3))
					POS_2, PLAY_2, NAV_2, DEM_2= elem['Position'], elem['PlayForm'], elem['NaviLink'], elem['Demand']
					SHORT = elem['playlist'][0] if 'playlist' in elem and len(elem.get('playlist', [])[0]) > 0 else elem
					SECTION = {k:v for k,v in SHORT.items() if k[:6] not in ['jwpseg', 'AdMark']}
					debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
					debug_MS(f"(navigator.DetailDescription[4]) no.04 ### POS : {str(POS_2)} || PLAY : {PLAY_2} || DEMAND : {DEM_2} || ELEM-04 : {SECTION} ###")
					markID_2 = SHORT['mediaid'] if SHORT.get('mediaid', '') else SHORT['Id'] if SHORT.get('Id', '') else 'Unknown-ID'
					TITLE_2 = (cleaning(SHORT.get('title')) or cleaning(SHORT.get('Title')))
					THUMB_2 = SHORT['image'] if SHORT.get('image', '') else None
					if THUMB_2 is None and SHORT.get('images', '') and len(SHORT['images']) > 0:
						THUMB_2 = [vid.get('src', []) for vid in SHORT.get('images', {}) if vid.get('type')[:5] == 'image'][-1]
					PUBLISHED = (SHORT.get('pubdate', None) or SHORT.get('PublishedUtc', None))
					if PUBLISHED:
						if str(PUBLISHED).isdigit():
							LOCALstart = get_Local_DT(datetime(1970, 1, 1) + timedelta(seconds=SHORT['pubdate']))
							AIRED_2 = LOCALstart.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('-', '•', ':')
							BEGINS_2 = LOCALstart.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
							if KODI_ov20:
								BEGINS_2 = LOCALstart.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
						else:
							LOCALstart = get_Local_DT(SHORT['PublishedUtc'][:19], 'FULLTIME')
							AIRED_2 = LOCALstart.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('-', '•', ':')
							BEGINS_2 = LOCALstart.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
							if KODI_ov20:
								BEGINS_2 = LOCALstart.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
					DESC_2 = (cleaning(SHORT.get('description', '')) or cleaning(SHORT.get('Description', '')))
					DURATION_2 = (SHORT.get('duration', 0) or SHORT.get('DurationSeconds', 0))
					if DURATION_2 != 0: DURATION_2 = "{0:.0f}".format(DURATION_2)
					COMBI_FOURTH.append([int(POS_2), markID_2, TITLE_2, THUMB_2, NAV_2, BEGINS_2, AIRED_2, DESC_2, DURATION_2])
	if COMBI_FOURTH or RESULT_ONE:
		RESULT_TWO = [e + f for e in RESULT_ONE for f in COMBI_FOURTH if e[5] == f[4]] # Zusammenführung von Liste1 und Liste2 - wenn der LINK überein stimmt !!!
		#log("++++++++++++++++++++++++")
		#log("(navigator.listArticles[5]) no.05 XXXXX RESULT_TWO-05 : {} XXXXX".format(str(RESULT_TWO)))
		#log("++++++++++++++++++++++++")
		for da in sorted(RESULT_TWO, key=lambda k: int(k[0]), reverse=False): # Liste1 = 0-14 oder 0-10|| Liste2 = 15-23 oder 11-19
			debug_MS("---------------------------------------------")
			debug_MS(f"(navigator.listResults[5]) no.05 ### Anzahl = {str(len(da))} || Eintrag : {str(da)} ###")
			STARTING, Note_1, Note_2, Note_3, Note_4, Note_5 = ("" for _ in range(6))
			aired, year = (None for _ in range(2))
			if len(da) > 20: ### Liste1+Liste2 ist grösser als Nummer:20 ###
				'''
				Liste-1_SHORT = num1, form1, mediaId1, title1, thumb1, link1, meta1, aired1, desc1, duration1, tagline1 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10]
				Liste-2_SHORT = num3, mediaId2, title2, thumb2, link2, begins, aired2, desc2, duration2 = da[11], da[12], da[13], da[14], da[15], da[16], da[17], da[18], da[19]
				Liste-1_LONG = num1, form1, mediaId1, title1, thumb1, link1, meta1, aired1, desc1, duration1, tagline1, num3, form3, link3, mediaId3 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11], da[12], da[13], da[14]
				Liste-2_LONG = num3, mediaId2, title2, thumb2, link2, begins, aired2, desc2, duration2 = da[15], da[16], da[17], da[18], da[19], da[20], da[21], da[22], da[23]
				'''
				Form1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = da[1], da[3], da[4], da[6], da[7], da[8], da[9], da[10]
				episID, Thumb2, begins, Aired2, Desc2, Duration2 = da[16], da[18], da[20], da[21], da[22], da[23]
			elif 16 <= len(da) <= 20: ### Liste1+Liste2 liegt zwischen Nummer:16-20 ###
				Form1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = da[1], da[3], da[4], da[6], da[7], da[8], da[9], da[10]
				episID, Thumb2, begins, Aired2, Desc2, Duration2 = da[12], da[14], da[16], da[17], da[18], da[19]
			elif 12 <= len(da) <= 15: ### Liste1 liegt zwischen Nummer:12-15 und Liste2 ist AUS ###
				Form1, Media1, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline, Form2, Media2 = da[1], da[2], da[3], da[4], da[6], da[7], da[8], da[9], da[10], da[12], da[14]
				episID = Media1 if Media1 != '00' else Media2.split('media/')[1].split('?poster')[0] if 'media/' in Media2 else Media2.split('clips/')[1]
				Thumb2, begins, Aired2, Desc2, Duration2 = None, None, None, "", 0
			elif len(da) <= 11: ### Liste1 ist kleiner als Nummer:12 und Liste2 ist AUS ###
				Form1, episID, title, Thumb1, producer, Aired1, Desc1, Duration1, tagline = da[1], da[2], da[3], da[4], da[6], da[7], da[8], da[9], da[10]
				Thumb2, begins, Aired2, Desc2, Duration2 = None, None, None, "", 0
			duration = Duration2 if Duration2 != 0 else Duration1 if Duration1 != 0 else 0
			image = Thumb2 if Thumb2 else Thumb1 if Thumb1 else None
			if producer:
				Note_1 = translation(30641).format(producer)
			if Aired1 or Aired2:
				STARTING = Aired2 if 16 <= len(da) <= 24 and Aired2 else Aired1
				Note_2 = translation(30642).format(STARTING) if Form1 == 'AUDIO' else translation(30643).format(STARTING)
				aired, year = STARTING[0:10].replace('-', '.'), STARTING[6:10]
			if Note_1 != "" or Note_2 != "":
				Note_3 = '[CR]'
			Note_4 = Desc2 if 16 <= len(da) <= 24 and len(Desc2) > len(Desc1) else Desc1
			Note_5 = '[B][COLOR magenta] ♫[/COLOR][/B]' if Form1 == 'AUDIO' else ""
			uvz = build_mass({'mode': 'playMedia', 'url': episID})
			plot = Note_1+Note_2+Note_3+Note_4
			name = title+Note_5
			debug_MS(f"(navigator.listResults[5]) no.05 ##### POS : {str(da[0])} || NAME : {name} || mediaID : {episID} || TIME : {STARTING} || BEGINS : {str(begins)} #####")
			debug_MS(f"(navigator.listResults[5]) no.05 ##### TAGLINE : {str(tagline)} || DURATION : {str(duration)} || THUMB : {str(image)} #####")
			for method in getSorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			LEM = xbmcgui.ListItem(name)
			if plot in ['', 'None', None]: plot = "..."
			if KODI_ov20:
				vinfo = LEM.getVideoInfoTag()
				vinfo.setTitle(re.sub('(\[B\]|\[/B\])', '', name))
				vinfo.setTagLine(tagline)
				vinfo.setPlot(plot)
				if str(duration).isdigit(): vinfo.setDuration(int(duration))
				if begins: LEM.setDateTime(begins)
				if aired: vinfo.setFirstAired(aired)
				if str(year).isdigit(): vinfo.setYear(int(year))
				vinfo.setGenres(['News'])
				vinfo.setStudios(['Der Spiegel'])
				vinfo.setMediaType('movie')
			else:
				vinfo = {}
				vinfo['Title'] = re.sub('(\[B\]|\[/B\])', '', name)
				vinfo['Tagline'] = tagline
				vinfo['Plot'] = plot
				if str(duration).isdigit(): vinfo['Duration'] = duration
				if begins: vinfo['Date'] = begins
				if aired: vinfo['Aired'] = aired
				if str(year).isdigit(): vinfo['Year'] = year
				vinfo['Genre'] = 'News'
				vinfo['Studio'] = 'Der Spiegel'
				vinfo['Mediatype'] = 'movie'
				LEM.setInfo(type='Video', infoLabels=vinfo)
			LEM.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
			if image and useThumbAsFanart and image != icon and not artpic in image:
				LEM.setArt({'fanart': image})
			LEM.setProperty('IsPlayable', 'true')
			LEM.setContentLookup(False)
			LEM.addContextMenuItems([(translation(30654), 'Action(Queue)')])
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uvz, listitem=LEM)
	else:
		debug_MS("(navigator.listArticles[4]) ##### Keine ARTICLES-LIST - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30521).format('WORK'), translation(30522), icon, 8000)
	debug_MS("+++++++++++++++++++++++++++++++++++++++++++++")
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSubstances(MURLS):
	COMBI_DETAILS, COMBI_INQUIRY = ([] for _ in range(2))
	COMBI_DETAILS = getMultiData(MURLS)
	if COMBI_DETAILS:
		for num, PLAY_3, WLINK_3, DDURL_3, each in COMBI_DETAILS:
			if each is not None:
				AREA, DATA_2, JSURL_2 = (None for _ in range(3))
				if PLAY_3 == 'VIDEO':
					AREA = re.compile(r'<div data-area="presentation_element>video">(.+?)data-sara-component=', re.S).findall(each)
					JWID_2 = re.compile('"(?:jwplayerMedia|media)Id":"([^"]+?)",', re.S).findall(AREA[0].replace('&#34;', '"')) if AREA else None
					JSURL_2 = f"https://vcdn01.spiegel.de/v2/media/{JWID_2[0]}?poster_width=1280&sources=hls,dash,mp4" if JWID_2 else None
				elif PLAY_3 == 'AUDIO':
					AREA = re.compile(r'(?:<div data-area="presentation_element>podlove">|<aside aria-label="Artikel zum Hören")(.+?)(?:data-sara-component=|data-area="playlist_button")', re.S).findall(each)
					JWID_2 = re.compile('x-audio-omny="([^"]+?)"', re.S).findall(AREA[0]) if AREA else None
					DATA_2 = base64.b64decode(JWID_2[0]) if JWID_2 else None
					CLIP_2 = re.compile('"omnystudioClipId":"([^"]+?)",', re.S).findall(py3_dec(DATA_2).replace('&#34;', '"')) if DATA_2 else None
					JSURL_2 = f"https://omny.fm/api/orgs/{COMPANY_ID}/clips/{CLIP_2[0]}" if CLIP_2 else None
				CONTENT = AREA[0].replace('&#34;', '"') if AREA else 'EntryNotFound'
				debug_MS(f"(navigator.listSubstances[3]) no.03 ### POS : {str(num)} || PLAY : {PLAY_3} || EACH-03 : {str(CONTENT)} ###")
				if JSURL_2 and DDURL_3:
					COMBI_INQUIRY.append([int(num), PLAY_3, WLINK_3, JSURL_2])
	return COMBI_INQUIRY

def listPlaylists():
	debug_MS("(navigator.listPlaylists) ------------------------------------------------ START = listPlaylists -----------------------------------------------")
	addDir(translation(30631), icon, {'url': BASE_YT.format(CHANNEL_CODE, 'UU1w6pNGiiLdZgyNpXUnA4Zw'), 'extras': 'YT_FOLDER'}, tag='Neu: DER SPIEGEL')
	playlists = get_videos(f"https://www.youtube.com/{CHANNEL_NAME}/playlists", 'https://www.youtube.com/youtubei/v1/browse', 'gridPlaylistRenderer', None, 1) # mit "get_videos" die Playlisten eines Channels abrufen
	for item in playlists:
		debug_MS(f"(navigator.listPlaylists[1]) XXXXX ENTRY-01 : {str(item)} XXXXX")
		title = cleaning(item['title']['runs'][0]['text'])
		PID = item['playlistId']
		photo = item['thumbnail']['thumbnails'][0]['url'].split('?sqp=')[0].replace('hqdefault', 'maxresdefault')
		if title.lower().startswith(('rocker', 'jaafars', 'spiegel tv vor 20', 'sport')):
			photo = item['thumbnail']['thumbnails'][0]['url'].split('?sqp=')[0]
		numbers = str(item['videoCountText']['runs'][0]['text']) if item.get('videoCountText', '') and item['videoCountText'].get('runs', '') and item['videoCountText']['runs'][0].get('text', '') else None
		name = translation(30632).format(title, numbers) if numbers is not None else translation(30633).format(title)
		addDir(name, photo, {'url': BASE_YT.format(CHANNEL_CODE, PID), 'extras': 'YT_FOLDER'}, tag='Playlist: Offizieller YouTube Kanal von SPIEGEL TV und DER SPIEGEL')
	xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)

def playMedia(PLID):
	debug_MS("(navigator.playMedia) -------------------------------------------------- START = playMedia --------------------------------------------------")
	MEDIAS = [] # https://omny.fm/api/orgs/5ac1e950-45c7-4eb7-87c0-aa0f018441b8/clips/6a92c18a-3ce2-49a4-9c87-b01a0144dadc
	M3U8_FILE, STREAM, QUALITY, FINAL_URL = (False for _ in range(4)) # https://vcdn01.spiegel.de/v2/media/ed2L0yL7?sources=hls,dash,mp4
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	NEW_URL = f"https://vcdn01.spiegel.de/v2/media/{PLID}?sources=hls,dash,mp4" if len(PLID) < 18 else f"https://omny.fm/api/orgs/{COMPANY_ID}/clips/{PLID}"
	debug_MS(f"(navigator.playMedia) ### NEW_URL = {NEW_URL} ###")
	DATA = getUrl(NEW_URL)
	if NEW_URL.startswith('https://vcdn01') and DATA.get('playlist', '') and DATA.get('playlist', {})[0].get('sources', ''):
		for source in DATA['playlist'][0]['sources']:
			TYPE = (source.get('type', 'UNKNOWN') or 'UNKNOWN')
			VIDEO = (source.get('file', None) or None)
			if TYPE.lower() == 'application/vnd.apple.mpegurl' and VIDEO and 'm3u8' in VIDEO:
				M3U8_FILE = VIDEO
			if TYPE.lower() == 'video/mp4' and VIDEO and 'mp4' in VIDEO:
				HEIGHT = (source.get('height', 0) or 0)
				MEDIAS.append({'url': VIDEO, 'mimeType': TYPE.lower(), 'height': HEIGHT})
				MEDIAS = sorted(MEDIAS, key=lambda h: int(h['height']), reverse=True)
		if MEDIAS: 	debug_MS(f"(navigator.playMedia[1]) MP4 ### SORTED_LIST : {str(MEDIAS)} ###")
		if (enableINPUTSTREAM or prefSTREAM == '0') and M3U8_FILE:
			STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
			TEXT = 'Inputstream (hls)' if enableINPUTSTREAM else 'Standard (m3u8)'
			debug_MS(f"(navigator.playMedia[2]) ***** TAKE - {TEXT} - FILE : {M3U8_FILE} *****")
			MIME, QUALITY, FINAL_URL = 'application/vnd.apple.mpegurl', 'AUTO', M3U8_FILE
		if not FINAL_URL and MEDIAS:
			for item in MEDIAS:
				if not enableINPUTSTREAM and prefSTREAM == '1' and item['height'] == prefQUALITY:
					debug_MS(f"(navigator.playMedia[3]) ***** TAKE - (mp4) - FILE : {item['url']} *****")
					STREAM, MIME, QUALITY, FINAL_URL = 'MP4', 'video/mp4', str(item['height'])+'p', item['url']
		if not FINAL_URL and MEDIAS:
			log("(navigator.playMedia[4]) !!!!! KEINEN passenden Stream gefunden --- nehme jetzt den Reserve-Stream-MP4 !!!!!")
			QUALITY = str(MEDIAS[0]['height'])+'p' if MEDIAS[0]['height'] != 0 else 'Unknown'
			STREAM, MIME, FINAL_URL = 'MP4', 'video/mp4', MEDIAS[0]['url']
	elif NEW_URL.startswith('https://omny.fm') and DATA.get('AudioUrl', ''):
		actual_time = int(round(time.time())) # UTC Datetime now
		debug_MS(f"(navigator.playMedia[1]) ***** TAKE - (mp3) - FILE : {DATA['AudioUrl']}?d={str(actual_time)}&utm_source=CustomPlayer1 *****")
		STREAM, MIME, QUALITY, FINAL_URL = 'MP3', 'audio/mp3', 'AUTO', f"{DATA['AudioUrl']}?d={str(actual_time)}&utm_source=CustomPlayer1"
	if FINAL_URL and STREAM:
		LSM = xbmcgui.ListItem(path=FINAL_URL)
		LSM.setMimeType(MIME)
		if ADDON_operate('inputstream.adaptive') and STREAM in ['HLS', 'MPD']:
			LSM.setProperty('inputstream', 'inputstream.adaptive')
			if KODI_un21: # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
				LSM.setProperty('inputstream.adaptive.manifest_type', STREAM.lower())
			if KODI_ov20:
				LSM.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={get_userAgent()}")
			else: # DEPRECATED ON Kodi v20, please use 'inputstream.adaptive.manifest_headers' instead.
				LSM.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={get_userAgent()}")
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log(f"(navigator.playMedia) [{QUALITY}] {STREAM}_stream : {FINAL_URL} ")
	else:
		failing(f"(navigator.playMedia) ##### Abspielen des Streams NICHT möglich ##### URL : {NEW_URL} #####\n ########## KEINEN passenden Stream-Eintrag gefunden !!! ##########")
		return dialog.notification(translation(30521).format('STREAM'), translation(30527), icon, 8000)

def addDir(name, image, params={}, tag='...', folder=True):
	if params.get('extras') == 'YT_FOLDER': u = params.get('url')
	else: u = build_mass(params)
	liz = xbmcgui.ListItem(name)
	if KODI_ov20:
		vinfo = liz.getVideoInfoTag()
		vinfo.setTitle(name), vinfo.setTagLine(tag), vinfo.setStudios(['Der Spiegel'])
	else:
		liz.setInfo(type='Video', infoLabels={'Title': name, 'Tagline': tag, 'Studio': 'Der Spiegel'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)
