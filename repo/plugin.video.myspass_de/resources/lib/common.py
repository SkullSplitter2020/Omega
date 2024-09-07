# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import time
from datetime import datetime, timedelta
import io
import gzip
import difflib
from urllib.parse import parse_qsl, urlencode, quote, quote_plus, unquote, unquote_plus
from urllib.request import build_opener


HOST_AND_PATH               = sys.argv[0]
ADDON_HANDLE                = int(sys.argv[1])
dialog                                   = xbmcgui.Dialog()
addon                                   = xbmcaddon.Addon()
addon_id                             = addon.getAddonInfo('id')
addon_name                       = addon.getAddonInfo('name')
addon_version                    = addon.getAddonInfo('version')
addonPath                           = xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                              = xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
channelFavsFile                  = os.path.join(dataPath, 'favorites_MYSPASS.json')
WORKFILE                           = os.path.join(dataPath, 'episode_data.json')
defaultFanart                      = os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon                                      = os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic                                    = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
alppic                                   = os.path.join(addonPath, 'resources', 'media', 'alphabet', '').encode('utf-8').decode('utf-8')
useThumbAsFanart            = addon.getSetting('useThumbAsFanart') == 'true'
enableADJUSTMENT           = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                          = (xbmc.LOGINFO if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20                         = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
BASE_LONG                        = 'https://www.myspass.de/'
BASE_URL                           = 'https://www.myspass.de'

xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

def py3_dec(d, nom='utf-8', ign='ignore'):
	if isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return addon.getLocalizedString(id)

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=xbmc.LOGINFO):
	return xbmc.log('[{} v.{}]{}'.format(addon_id, addon_version, str(msg)), level)

def get_userAgent(REV='109.0', VER='112.0'):
	base = 'Mozilla/5.0 {} Gecko/20100101 Firefox/'+VER
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format(f'(X11; Linux arm64; rv:{REV})') # ARM based Linux
		return base.format(f'(X11; Linux x86_64; rv:{REV})') # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format(f'(Windows NT 10.0; Win64; x64; rv:{REV})') # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format(f'(Macintosh; Intel Mac OS X 10.15; rv:{REV})') # Mac OSX
	return base.format(f'(X11; Linux x86_64; rv:{REV})') # x64 Linux

def getUrl(url, headers=None, data=None, agent=get_userAgent()):
	opener = build_opener()
	opener.addheaders = [('User-Agent', agent), ('Accept-Encoding', 'gzip, identity')]
	ANSWER = None
	try:
		if headers: opener.addheaders = headers
		response = opener.open(url, data, timeout=30)
		if response.info().get('Content-Encoding') == 'gzip':
			ANSWER = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			ANSWER = py3_dec(response.read())
	except Exception as e:
		failing(f"(common.getUrl) ERROR - ERROR - ERROR ##### url : {url} === error : {str(e)} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 10000)
		return sys.exit(0)
	return ANSWER

def get_Seconds(info):
	try:
		info = re.sub('[a-zA-Z]', '', info)
		secs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(info.split(':'))))
		return "{0:.0f}".format(secs)
	except: return '0'

def getSorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_EPISODE, xbmcplugin.SORT_METHOD_DATE]

def cleanPlaylist():
	playlist = xbmc.PlayList(1)
	playlist.clear()
	return playlist

def cleaning(text):
	if text is not None:
		for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
					("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
					('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
					('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
					('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
					('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
					('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
					('u00c4', 'Ä'), ('u00e4', 'ä'), ('u00d6', 'Ö'), ('u00f6', 'ö'), ('u00dc', 'Ü'), ('u00fc', 'ü'), ('u00df', 'ß'), ('u00e0', 'à'), ('u00e1', 'á'), ('u00e9', 'é'), # Line = php-Codes clear
					('u00b4', '´'), ('u0060', '`'), ('u201c', '“'), ('u201d', '”'), ('u201e', '„'), ('u201f', '‟'), ('u2013', '-'), ("u2018", "‘"), ("u2019", "’"), # Line = php-Codes clear
					('Ã¤', 'ä'), ('Ã„', 'Ä'), ('Ã¶', 'ö'), ('Ã–', 'Ö'), ('Ã¼', 'ü'), ('Ãœ', 'Ü'), ('ÃŸ', 'ß'), ('â€ž', '„'), ('â€œ', '“'), ('â€™', '’'), ('â€“', '–'), ('Ã¡', 'á'), ('Ã©', 'é'), ('Ã¨', 'è')): # Line = xml-writing-Umlaut clear
					text = text.replace(*n)
		text = text.strip()
	return text

def cleanPhoto(img): # UNICODE-Zeichen für Browser übersetzen - damit Fotos angezeigt werden
	img = quote(img, safe='/:')
	img = img if img.startswith('http') else 'https:'+img if img.startswith('//') else BASE_URL+img
	if img.count('%') == img.count('%25'): # It's double QUOTED (Umlaute z.B. 'ö' zu falsch='%25C3%25B6' richtig='%C3%B6')
		img = unquote(img)
	return img.strip()

def similar(a, b, max_similarity=0.85):
	if difflib.SequenceMatcher(None, a, b).ratio() >= max_similarity:
		debug_MS(f"(common.similar) ##### fullURL = {a} || URL-2 = {b} || SIMILAR % = {str(difflib.SequenceMatcher(None, a, b).ratio())} #####")
		return True
	return False

def getVideodata(VideoID):
	# https://www.myspass.de/includes/apps/video/getvideometadataxml.php?id=886
	show, name, plot, stream = ("" for _ in range(4))
	seasonNR, episodeNR, image, starting, begins = (None for _ in range(5))
	duration = '0'
	url = f'{BASE_URL}/includes/apps/video/getvideometadataxml.php?id={VideoID}'
	debug_MS(f"(common.getVideodata) ### URL : {url} ###")
	content = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS(f"(common.getVideodata) CONTENT = {str(content)}")
	debug_MS("++++++++++++++++++++++++")
	TVS = re.compile('<format><!\\[CDATA\\[(.+?)\\]\\]></format>', re.S).findall(content)
	if TVS: show = cleaning(TVS[0])
	TTL = re.compile('<title><!\\[CDATA\\[(.+?)\\]\\]></title>', re.S).findall(content)
	if TTL: name = cleaning(TTL[0])
	SEAS = re.compile('<season><!\\[CDATA\\[(.+?)\\]\\]></season>', re.S).findall(content)
	if SEAS: seasonNR = SEAS[0]
	EPIS = re.compile('<episode><!\\[CDATA\\[(.+?)\\]\\]></episode>', re.S).findall(content)
	if EPIS: episodeNR = EPIS[0]
	DESC = re.compile('<description><!\\[CDATA\\[(.+?)\\]\\]></description>', re.S).findall(content)
	if DESC: plot = cleaning(DESC[0])
	DUR = re.compile('<duration><!\\[CDATA\\[(.+?)\\]\\]></duration>', re.S).findall(content)
	if DUR: duration = get_Seconds(DUR[0])
	IMG = re.compile('<imagePreview><!\\[CDATA\\[(.+?)\\]\\]></imagePreview>', re.S).findall(content)
	if IMG: image = IMG[0]
	BC_DATE = re.compile('<broadcast_date><!\\[CDATA\\[(.+?)\\]\\]></broadcast_date>', re.S).findall(content)
	BC_TIME = re.compile('<broadcast_time><!\\[CDATA\\[(.+?)\\]\\]></broadcast_time>', re.S).findall(content)
	if BC_DATE and BC_TIME:
		try:
			fullDATE = BC_DATE[0][:10]+'T'+BC_TIME[0][:8]
			available = datetime(*(time.strptime(fullDATE, '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-13T22:15:00
			starting = available.strftime('%a{0} %d{0}%m{0}%Y').format('.')
			for sd in (('Mon', translation(32101)), ('Tue', translation(32102)), ('Wed', translation(32103)), ('Thu', translation(32104)), ('Fri', translation(32105)), ('Sat', translation(32106)), ('Sun', translation(32107))): starting = starting.replace(*sd)
			begins = available.strftime('%d{0}%m{0}%Y').format('.') # 09.03.2023 / OLDFORMAT
			if KODI_ov20:
				begins = available.strftime('%Y{0}%m{0}%dT%H{1}%M').format('-', ':') # 2023-03-09T12:30:00 / NEWFORMAT
		except: pass
	VID = re.compile('<url_flv><!\\[CDATA\\[(.+?)\\]\\]></url_flv>', re.S).findall(content)
	if VID:
		stream = VID[0]
		grps = re.search(r'/myspass2009/\d+/(\d+)/(\d+)/(\d+)/', stream)
		for group in grps.groups() if grps else []:
			videoINT, groupINT = int(VideoID), int(group)
			if groupINT > videoINT:
				try: stream = stream.replace(group, unicode(groupINT // videoINT))
				except NameError: stream = stream.replace(group, str(groupINT // videoINT))
	return (show, name, seasonNR, episodeNR, plot, duration, image, starting, begins, stream)

params = dict(parse_qsl(sys.argv[2][1:]))
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
pict = unquote_plus(params.get('pict', ''))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', ''))
origSERIE = unquote_plus(params.get('origSERIE', ''))
extras = unquote_plus(params.get('extras', 'standard'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
