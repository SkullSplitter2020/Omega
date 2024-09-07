# -*- coding: utf-8 -*-

from .common import *


def getHTML(url, method='GET', REF=None, cookies=None, allow_redirects=True, stream=None, data=None, json=None):
	simple = requests.Session()
	REACTION = None
	try:
		response = simple.get(url, headers={'User-Agent': get_userAgent()}, allow_redirects=allow_redirects, verify=verify_connection, stream=stream, timeout=30)
		REACTION = response.json() if method == 'GET' else response.text
	except requests.exceptions.RequestException as e:
		failing(f"(mediatools.getHTML) ERROR - ERROR - ERROR : ##### url : {url} === error : {str(e)} #####")
		dialog.notification(translation(30521).format('URL', ''), translation(30523).format(str(e)), icon, 12000)
		return sys.exit(0)
	return REACTION

def preparefiles(url, name, XTRA, rotation):
	debug_MS("(mediatools.preparefiles) -------------------------------------------------- START = tolibrary --------------------------------------------------")
	if mediaPATH == "":
		return dialog.ok(addon_id, translation(30505))
	elif mediaPATH != "" and ADDON_operate('service.cron.autobiblio'):
		title = name
		if XTRA in ['Series', 'Movies']:
			title += f"  ({XTRA.replace('es', 'e')})"
			NEW_SOURCE = quote_plus(f"{mediaPATH}{fixPathSymbols(name)}")
			if newMETHOD:
				url = f"{url}@@{XTRA}"
				NEW_SOURCE = quote_plus(f"{mediaPATH}{XTRA}{os.sep}{fixPathSymbols(name)}")
		elif XTRA not in ['Series', 'Movies']:
			title += f"  ({XTRA})"
			XTRA = XTRA.replace('Jahr ', '')
			url = f"{url}@@{XTRA}"
			NEW_SOURCE = quote_plus(f"{mediaPATH}{fixPathSymbols(name)}{os.sep}{XTRA}")
			if newMETHOD:
				NEW_SOURCE = quote_plus(f"{mediaPATH}Series{os.sep}{fixPathSymbols(name)}{os.sep}{XTRA}")
		NEW_URL = f"{sys.argv[0]}?mode=generatefiles&url={url}&name={name}"
		NEW_NAME, NEW_URL = quote_plus(name), quote_plus(NEW_URL)
		debug_MS(f"(mediatools.preparefiles) ### NEW_NAME : {NEW_NAME} ###")
		debug_MS(f"(mediatools.preparefiles) ### NEW_URL : {NEW_URL} ###")
		debug_MS(f"(mediatools.preparefiles) ### NEW_SOURCE : {NEW_SOURCE} ###")
		xbmc.executebuiltin(f"RunPlugin(plugin://service.cron.autobiblio/?mode=adddata&name={NEW_NAME}&stunden={rotation}&url={NEW_URL}&source={NEW_SOURCE})")
		return dialog.notification(translation(30571), translation(30572).format(title, str(rotation)), icon, 15000)

def querypages(url, TVFOL, EPATH, POS=200):
	DATA_UNO = getHTML(f"{url}&page=1")
	debug_MS(f"(mediatools.generatefiles[2]) SUCCESSFULLY CREATED XXXXX URL_ONE-02 : {TVFOL} XXXXX ")
	debug_MS(f"(mediatools.generatefiles[3]) no.03 ### EP-PATH : {str(EPATH)} ###")
	debug_MS(f"(mediatools.generatefiles[4]) no.04 ### URL-TWO : {url}&page=1 ###")
	if DATA_UNO.get('movies', '') and DATA_UNO.get('movies', {}).get('items', ''):
		DATA_UNO = DATA_UNO['movies']
	for item in DATA_UNO.get('items', []): yield item
	ALLPAGES = int(DATA_UNO.get('total', [])) // int(POS) if DATA_UNO.get('total', '') else -1
	debug_MS(f"(mediatools.querypages) ### Total-Items : {str(DATA_UNO.get('total', None))} || Result of PAGES : {str(ALLPAGES+1)} ###")
	for page in range(2, ALLPAGES+2, 1):
		DATA_DUE = getHTML(f"{url}&page={page}")
		debug_MS(f"(mediatools.generatefiles[5]) no.05 ### URL-TRES : {url}&page={page} ###")
		if DATA_DUE.get('movies', '') and DATA_DUE.get('movies', {}).get('items', ''):
			DATA_DUE = DATA_DUE['movies']
		for item in DATA_DUE.get('items', []): yield item

def generatefiles(BroadCast_URL, BroadCast_NAME):
	debug_MS("(mediatools.generatefiles) -------------------------------------------------- START = generatefiles --------------------------------------------------")
	debug_MS(f"(mediatools.generatefiles) ### BroadCast_URL = {BroadCast_URL} || BroadCast_NAME = {BroadCast_NAME} ###")
	if not enableLIBRARY or mediaPATH == "":
		return
	EPIS_ENTRIES = '[%22id%22,%22title%22,%22broadcastStartDate%22,%22catchupStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,'\
									'%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=200'
	COMBINATION = []
	pos_ESP = 0
	elem_IDD, elem_TAG = BroadCast_URL, None
	if '@@' in BroadCast_URL:
		elem_IDD = BroadCast_URL.split('@@', 1)[0]
		elem_TAG = BroadCast_URL.split('@@', 1)[1]
	if newMETHOD:
		if elem_TAG and elem_TAG in ['Series', 'Movies']:
			TVS_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, elem_TAG, fixPathSymbols(BroadCast_NAME), ''))
			EP_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, elem_TAG, fixPathSymbols(BroadCast_NAME), ''))
		elif elem_TAG and elem_TAG not in ['Series', 'Movies']:
			TVS_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, 'Series', fixPathSymbols(BroadCast_NAME), ''))
			EP_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, 'Series', fixPathSymbols(BroadCast_NAME), str(elem_TAG), ''))
		else:
			TVS_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, 'Series', fixPathSymbols(BroadCast_NAME), ''))
			EP_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, 'Series', fixPathSymbols(BroadCast_NAME), ''))
	else:
		if elem_TAG and elem_TAG not in ['Series', 'Movies']:
			TVS_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, fixPathSymbols(BroadCast_NAME), ''))
			EP_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, fixPathSymbols(BroadCast_NAME), str(elem_TAG), ''))
		else:
			TVS_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, fixPathSymbols(BroadCast_NAME), ''))
			EP_Path = xbmcvfs.translatePath(os.path.join(mediaPATH, fixPathSymbols(BroadCast_NAME), ''))
	url_1 = f"{API_URL}/formats/{str(elem_IDD)}?fields=[%22id%22,%22title%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22tabSeason%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22genres%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22,%22onlineDate%22,%22annualNavigation%22,%22seasonNavigation%22]"
	debug_MS(f"(mediatools.generatefiles[1]) PREPARE FOLDER FOR XXXXX URL_ONE-01 : {str(url_1)} XXXXX ")
	TVS_Info = xbmcvfs.translatePath(os.path.join(TVS_Path, 'tvshow.nfo'))
	if xbmcvfs.exists(TVS_Info):
		xbmcvfs.delete(TVS_Info)
		xbmc.sleep(100)
	if xbmcvfs.exists(EP_Path) and os.path.exists(EP_Path):
		shutil.rmtree(EP_Path, ignore_errors=True)
		xbmc.sleep(200)
	if not xbmcvfs.exists(EP_Path) and not os.path.exists(EP_Path):
		xbmcvfs.mkdirs(EP_Path)
	try:
		SHOW_DATA = getHTML(url_1)
		TVS_name = cleaning(SHOW_DATA['title'])
	except: return
	SERIES_IDD = str(SHOW_DATA['id'])
	TVS_studio, TVS_image, TVS_airdate = ("" for _ in range(3))
	TVS_studio = SHOW_DATA['station'].upper() if SHOW_DATA.get('station', '') else 'UNK'
	TVS_image = (cleanPhoto(SHOW_DATA.get('formatimageMoviecover169', '')) or cleanPhoto(SHOW_DATA.get('formatimageArtwork', '')) or IMG_series.format(SERIES_IDD))
	TVS_plot = get_Description(SHOW_DATA, 'TVS')
	if str(SHOW_DATA.get('onlineDate'))[:4] not in ['', 'None', '0', '1970']:
		TVS_airdate = str(SHOW_DATA['onlineDate'])[:10]
	if elem_TAG and elem_TAG not in ['Series', 'Movies']:
		if len(elem_TAG) == 4:
			url_2 = f"{API_URL}/movies?filter={{%22BroadcastStartDate%22:{{%22between%22:{{%22start%22:%22{elem_TAG}-01-01%2000:00:00%22,%22end%22:%22{elem_TAG}-12-31%2023:59:59%22}}}},%22FormatId%22:{SERIES_IDD}}}&fields={EPIS_ENTRIES}"
		elif 'Staffel ' in elem_TAG:
			url_2 = f"{API_URL}/movies?filter={{%22Season%22:{elem_TAG.split('Staffel ')[1]},%22FormatId%22:{SERIES_IDD}}}&fields={EPIS_ENTRIES}"
	else:
		url_2 = f"{API_URL}/movies?filter={{%22FormatId%22:{SERIES_IDD}}}&fields={EPIS_ENTRIES}"
	for vid in querypages(url_2, url_1, EP_Path):
		EP_tagline, EP_genre1, EP_genre2, EP_genre3, Note_1, Note_2, Note_3, Note_4, Note_5, Suffix_1, Suffix_2, EP_fsk, EP_yeardate, EP_studio, EP_airdate = ("" for _ in range(15))
		EP_season, EP_episode, EP_duration = ('0' for _ in range(3))
		TVS_title, EP_streamSD, EP_streamHD, startTIMES, startTITLE = (None for _ in range(5))
		EP_genreLIST = []
		EP_idd = vid.get('id', '00')
		EP_title = cleaning(vid['title'])
		EP_tagline = cleaning(vid.get('teaserText', ''))
		EP_duration = get_RunTime(vid['duration'], 'MINUTES') if vid.get('duration', '') else '0'
		if vid.get('format', ''):
			SHORTY = vid['format']
			TVS_title = cleaning(SHORTY['title']) if SHORTY.get('title', '') else None
			if TVS_title is None: TVS_title = cleaning(SHORTY['seoUrl']).replace('-', ' ').title() if SHORTY.get('seoUrl', '') else None
			if TVS_title is None: continue
			EP_studio = SHORTY['station'].upper() if SHORTY.get('station', '') else 'UNK'
			if SHORTY.get('genres', ''):
				EP_genreLIST = [cleaning(item) for item in SHORTY.get('genres', '')]
				if EP_genreLIST: EP_genreLIST = sorted(EP_genreLIST)
		else: continue
		if len(EP_genreLIST) > 0: EP_genre1 = EP_genreLIST[0]
		if len(EP_genreLIST) > 1: EP_genre2 = EP_genreLIST[1]
		if len(EP_genreLIST) > 2: EP_genre3 = EP_genreLIST[2]
		debug_MS("---------------------------------------------")
		debug_MS(f"(mediatools.generatefiles[5]) xxxxx ELEMENT-05 : {str(vid)} xxxxx")
		EP_protect = vid.get('isDrm', False)
		EP_PayFree = (vid.get('payed', True) or vid.get('free', True))
		if EP_PayFree is False and vodPremium is False and STATUS < 3:
			Note_1   = translation(30624).format(TVS_title)
			Note_2   = '   [COLOR skyblue](premium)[/COLOR][CR]'
			Suffix_2 = '     [COLOR deepskyblue](premium)[/COLOR]'
		else: Note_1 = translation(30624).format(TVS_title)+'[CR]'
		EP_season = re.sub('[a-zA-Z]', '', str(vid['season'])).zfill(2) if vid.get('season', '') else '0'
		EP_episode = re.sub('[a-zA-Z]', '', str(vid['episode'])).zfill(2) if vid.get('episode', '') else '0'
		if EP_season != '0' and EP_episode != '0': Note_3 = translation(30625).format(EP_season, EP_episode)
		elif EP_season == '0' and EP_episode != '0': Note_3 = translation(30626).format(EP_episode)
		if vid.get('manifest', '') and vid['manifest'].get('dash', ''): # Normal-Play with Pay-Account
			EP_streamSD = vid['manifest']['dash'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').replace('/p11114', '/p112').replace('manifest/tvnow', 'manifest/rtlplussd').replace('/0.ism', '/4000.ism').replace('/10000.ism', '/4000.ism').split('.mpd')[0]+'.mpd'
		if vid.get('manifest', '') and vid['manifest'].get('dashhd', ''): # HD-Play with Pay-Account
			EP_streamHD = vid['manifest']['dashhd'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').replace('/p11114', '/p112').replace('manifest/tvnow', 'manifest/rtlplushd').replace('/0.ism', '/10000.ism').replace('/4000.ism', '/10000.ism').split('.mpd')[0]+'.mpd'
		EP_STARTS = (vid.get('broadcastStartDate', None) or vid.get('catchupStartDate', None))
		if str(EP_STARTS)[:4].isdigit() and str(EP_STARTS)[:4] not in ['0', '1970']:
			broadcast = datetime(*(time.strptime(EP_STARTS[:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2015-10-07 05:10:00
			startTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			for sd in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))): startTIMES = startTIMES.replace(*sd)
			startTITLE = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
		Note_4 = translation(30627).format(str(startTIMES))+'[CR]' if startTIMES else '[CR]'
		if showDATE and startTITLE:
			Suffix_1 = translation(30628).format(str(startTITLE))
		if str(vid.get('fsk')).isdigit():
			EP_fsk = translation(30630).format(str(vid['fsk'])) if str(vid.get('fsk')) != '0' else translation(30631)
		if str(vid.get('productionYear'))[:4].isdigit() and str(vid.get('productionYear'))[:4] not in ['0', '1970']:
			EP_yeardate = str(vid['productionYear'])[:4]
		EP_airdate = (str(vid.get('broadcastStartDate', ''))[:10] or str(vid.get('broadcastPreviewStartDate', ''))[:10])
		EP_cover = IMG_coverdvd.format(SERIES_IDD)
		EP_image = IMG_movies.format(EP_idd)
		Note_5 = get_Description(vid) # Description of the Video
		EP_LONG_title = EP_title+Suffix_1+Suffix_2
		EP_plot = Note_1+Note_2+Note_3+Note_4+Note_5
		pos_ESP += 1
		if newMETHOD and elem_TAG and elem_TAG == 'Movies':
			EP_SHORT_title = EP_title
		else:
			if EP_season != '0' and EP_episode != '0':
				EP_SHORT_title = f"S{EP_season}E{EP_episode}_{EP_title}"
			else:
				EP_episode = str(pos_ESP).zfill(2)
				EP_SHORT_title = f"S00E{EP_episode}_{EP_title}"
		if elem_TAG and elem_TAG not in ['Series', 'Movies']:
			EP_STREAM_ENTRIES = build_mass({'mode': 'listEpisodes', 'url': SERIES_IDD, 'extras': elem_TAG, 'xcode': EP_idd})
		else:
			EP_STREAM_ENTRIES = build_mass({'mode': 'listEpisodes', 'url': SERIES_IDD, 'extras': 'OneDirect', 'xcode': EP_idd})
		episodeFILE = fixPathSymbols(EP_SHORT_title)
		COMBINATION.append([episodeFILE, EP_LONG_title, TVS_title, EP_idd, EP_season, EP_episode, EP_tagline, EP_plot, EP_duration, EP_cover, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_STREAM_ENTRIES])
	if not COMBINATION: return
	else:
		if not xbmcvfs.exists(EP_Path) and not os.path.exists(EP_Path):
			xbmcvfs.mkdirs(EP_Path)
		if newMETHOD and elem_TAG and elem_TAG == 'Movies':
			for episodeFILE, EP_LONG_title, TVS_title, EP_idd, EP_season, EP_episode, EP_tagline, EP_plot, EP_duration, EP_cover, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_STREAM_ENTRIES in COMBINATION:
				nfo_MOVIE_string = xbmcvfs.translatePath(os.path.join(EP_Path, episodeFILE+'.nfo'))
				with io.open(nfo_MOVIE_string, 'w', encoding='utf-8') as textobj_MO:
					textobj_MO.write(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{0}</title>
    <originaltitle>{1}</originaltitle>
    <tagline>{4}</tagline>
    <plot>{5}</plot>
    <runtime>{6}</runtime>
    <thumb spoof="" cache="" aspect="poster" preview="{7}">{7}</thumb>
    <thumb spoof="" cache="" aspect="thumb" preview="{8}">{8}</thumb>
    <fanart>
        <thumb dim="1280x720" colors="" preview="{8}">{8}</thumb>
    </fanart>
    <mpaa>{9}</mpaa>
    <genre clear="true">{10}</genre>
    <genre>{11}</genre>
    <genre>{12}</genre>
    <year>{13}</year>
    <aired>{14}</aired>
    <studio clear="true">{15}</studio>
</movie>'''.format(EP_LONG_title, TVS_title, EP_season, EP_episode, EP_tagline, EP_plot, EP_duration, EP_cover, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio))
				streamfile = xbmcvfs.translatePath(os.path.join(EP_Path, episodeFILE+'.strm'))
				debug_MS(f"(mediatools.generatefiles[6]) MOVIES-no.06 ##### streamFILE : {cleaning(streamfile)} #####")
				file = xbmcvfs.File(streamfile, 'w')
				file.write(EP_STREAM_ENTRIES)
				file.close()
		else:
			for episodeFILE, EP_LONG_title, TVS_title, EP_idd, EP_season, EP_episode, EP_tagline, EP_plot, EP_duration, EP_cover, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_STREAM_ENTRIES in COMBINATION:
				nfo_EPISODE_string = xbmcvfs.translatePath(os.path.join(EP_Path, episodeFILE+'.nfo'))
				with io.open(nfo_EPISODE_string, 'w', encoding='utf-8') as textobj_EP:
					textobj_EP.write(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<episodedetails>
    <title>{0}</title>
    <showtitle>{1}</showtitle>
    <season>{2}</season>
    <episode>{3}</episode>
    <tagline>{4}</tagline>
    <plot>{5}</plot>
    <runtime>{6}</runtime>
    <thumb spoof="" cache="" aspect="" preview="{8}">{8}</thumb>
    <fanart>
        <thumb dim="1280x720" colors="" preview="{8}">{8}</thumb>
    </fanart>
    <mpaa>{9}</mpaa>
    <genre clear="true">{10}</genre>
    <genre>{11}</genre>
    <genre>{12}</genre>
    <year>{13}</year>
    <aired>{14}</aired>
    <studio clear="true">{15}</studio>
</episodedetails>'''.format(EP_LONG_title, TVS_title, EP_season, EP_episode, EP_tagline, EP_plot, EP_duration, EP_cover, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio))
				streamfile = xbmcvfs.translatePath(os.path.join(EP_Path, episodeFILE+'.strm'))
				debug_MS(f"(mediatools.generatefiles[6]) EPISODES-no.06 ##### streamFILE : {cleaning(streamfile)} #####")
				file = xbmcvfs.File(streamfile, 'w')
				file.write(EP_STREAM_ENTRIES)
				file.close()
			nfo_SERIE_string = xbmcvfs.translatePath(os.path.join(TVS_Path, 'tvshow.nfo'))
			with io.open(nfo_SERIE_string, 'w', encoding='utf-8') as textobj_TVS:
				textobj_TVS.write(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>{0}</title>
    <showtitle>{0}</showtitle>
    <season></season>
    <episode></episode>
    <plot>{1}</plot>
    <thumb spoof="" cache="" aspect="" preview="{2}">{2}</thumb>
    <thumb spoof="" cache="" season="" type="season" aspect="" preview="{2}">{2}</thumb>
    <fanart>
        <thumb dim="1280x720" colors="" preview="{2}">{2}</thumb>
    </fanart>
    <genre clear="true">{3}</genre>
    <genre>{4}</genre>
    <genre>{5}</genre>
    <year>{6}</year>
    <aired>{7}</aired>
    <studio clear="true">{8}</studio>
</tvshow>'''.format(TVS_name, TVS_plot, TVS_image, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, TVS_airdate, TVS_studio))
	debug_MS("(mediatools.generatefiles[7]) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX THE END OF 'generatefiles' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
