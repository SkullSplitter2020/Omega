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
from calendar import timegm as TGM
import base64
import requests
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
from concurrent.futures import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addon_desc						= addon.getAddonInfo('description')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
genpic									= os.path.join(addonPath, 'resources', 'media', 'genre', '').encode('utf-8').decode('utf-8')
PAGINATION						= int(addon.getSetting('max_pages'))+1
enableYOUTUBE				= addon.getSetting('youtube_channel') == 'true'
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableAUDIO						= addon.getSetting('audiostreams') == 'true'
enableINPUTSTREAM		= addon.getSetting('use_adaptive') == 'true'
prefSTREAM						= addon.getSetting('prefer_stream')
prefQUALITY						= {0: 1080, 1: 720, 2: 576, 3: 360}[int(addon.getSetting('prefer_quality'))]
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
COMPANY_ID					= '5ac1e950-45c7-4eb7-87c0-aa0f018441b8' # https://omny.fm/api/orgs/5ac1e950-45c7-4eb7-87c0-aa0f018441b8/clips/6a92c18a-3ce2-49a4-9c87-b01a0144dadc
CHANNEL_CODE				= 'UC1w6pNGiiLdZgyNpXUnA4Zw'
CHANNEL_NAME				= '@derspiegel'
BASE_YT								= 'plugin://plugin.video.youtube/channel/{}/playlist/{}/'
BASE_URL							= 'https://www.spiegel.de/'

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
	return xbmc.log(f"[{addon_id} v.{addon_version}]{str(msg)}", level)

def build_mass(body):
	return f"{HOST_AND_PATH}?{urlencode(body)}"

def get_userAgent(REV='109.0', VER='112.0'):
	base = f"Mozilla/5.0 {{}} Gecko/20100101 Firefox/{VER}"
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format(f"(X11; Linux arm64; rv:{REV})") # ARM based Linux
		return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format(f"(Windows NT 10.0; Win64; x64; rv:{REV})") # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format(f"(Macintosh; Intel Mac OS X 10.15; rv:{REV})") # Mac OSX
	return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux

def _header(REFERRER=None):
	header = {}
	header['Connection'] = 'keep-alive'
	header['Pragma'] = 'no-cache'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	if REFERRER:
		header['Referer'] = REFERRER
	return header

def getMultiData(MURLS, WAY='TEXT', method='GET', REF=None, fields=None):
	COMBI_NEW = []
	number = len(MURLS)
	def download(pos, clip, link, url, manager):
		response = manager.request(method, url, fields, headers=_header(REF), timeout=5, retries=3)
		if response and response.status in [200, 201, 202]:
			debug_MS(f"(common.getMultiData[1]) === POS : {str(pos)} === REQUESTED URL : {url} === REQUESTED HEADER : {_header(REF)} ===")
			if WAY == 'TEXT':
				return [pos, clip, link, url, py3_dec(response.data)]
			elif WAY == 'JS':
				return f'{{"Position":{str(pos)},"PlayForm":"{clip}","NaviLink":"{link}","Demand":"{url}",{py3_dec(response.data[1:-1])}}}'
		else:
			failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {str(pos)} === STATUS : {str(response.status)} === URL : {url} === DATA : {str(response.data)} #####")
			return [pos, clip, link, url, None] if WAY == 'TEXT' else '{"ERROR_occurred":true}'
	with ThreadPoolExecutor() as executor:
		connector = urllib3.PoolManager(maxsize=20, block=True)
		debug_MS("* * * * * * * * * * * * * * * * * * * * * * *")
		picker = [executor.submit(download, pos, clip, link, url, connector) for pos, clip, link, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(future.result()) if WAY == 'TEXT' else COMBI_NEW.append(json.loads(future.result()))
			except Exception as e:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {str(e)} #####")
				dialog.notification(translation(30521).format('DETAILS'), translation(30523).format(str(e)), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			matching = [flop for flop in COMBI_NEW[:] if flop[4] is None] if WAY == 'TEXT' else [flop for flop in COMBI_NEW[:] if flop.get('ERROR_occurred', '') is True]
			if len(matching) == number or len(matching) > 15:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return COMBI_NEW if WAY == 'TEXT' else json.dumps(COMBI_NEW, indent=2)

def getUrl(url, method='GET', REF=BASE_URL, headers=None, cookies=None, allow_redirects=True, verify=True, stream=None, data=None, json=None):
	simple = requests.Session()
	ANSWER = None
	try:
		response = simple.get(url, headers=_header(REF), allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
		ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
		debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {_header(REF)} ===")
	except requests.exceptions.RequestException as e:
		failing(f"(common.getUrl) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 10000)
		return sys.exit(0)
	return ANSWER

def ADDON_operate(IDD):
	check_1 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	check_2 = 'undone'
	if '"enabled":false' in check_1:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{{"addonid":"{IDD}", "enabled":true}}}}')
			failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
		check_2 = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{{"addonid":"{IDD}", "properties":["enabled"]}}}}')
	if '"error":' in check_1 or '"error":' in check_2:
		dialog.ok(addon_id, translation(30501).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT installiert !!! #####")
		return False
	if '"enabled":true' in check_1 or '"enabled":true' in check_2:
		return True
	if '"enabled":false' in check_2:
		dialog.ok(addon_id, translation(30502).format(IDD))
		failing(f"(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{IDD}* ist NICHT aktiviert !!! #####\n##### Eine automatische Aktivierung ist leider NICHT möglich !!! #####")
	return False

def get_Seconds(info):
	try:
		if 'min' in info.lower():
			info = re.sub('[a-zA-Z]', '', info)
			secs = int(info) * 60
		else:
			info = re.sub('[a-zA-Z]', '', info)
			secs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(info.split(':'))))
		return "{0:.0f}".format(secs)
	except: return 0

def get_Local_DT(indicator, event='EPOCHTIME'):
	utcDT = indicator
	if event == 'FULLTIME':
		fixed_format = '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':') # 2023-06-07T19:43:00.333Z
		utcDT = datetime(*(time.strptime(indicator, fixed_format)[0:6]))
	try:
		localDT = datetime.fromtimestamp(TGM(utcDT.timetuple()))
		assert utcDT.resolution >= timedelta(microseconds=1)
		localDT = localDT.replace(microsecond=utcDT.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		localDT = datetime.fromtimestamp(0) + timedelta(seconds=TGM(utcDT.timetuple()))
		localDT = localDT - timedelta(hours=datetime.timetuple(localDT).tm_isdst)
	return localDT

def getSorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_DATE]

def cleaning(text):
	if text is not None:
		for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
					("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
					('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
					('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
					('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
					('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
					('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
					('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
					('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
					('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '),
					("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
					('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ('\\"', '"')):
					text = text.replace(*n)
		text = text.strip()
	return text

params = dict(parse_qsl(sys.argv[2][1:]))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
limit = unquote_plus(params.get('limit', '0'))
extras = unquote_plus(params.get('extras', 'DEFAULT'))
