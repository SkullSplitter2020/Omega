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
import socket
import time
from datetime import datetime, timedelta
import base64
import requests
from urllib.parse import parse_qsl, urlencode, quote_plus, unquote_plus
from urllib.request import urlopen
from concurrent.futures import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


socket.setdefaulttimeout(30)
HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addonPath							= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath								= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
WORKFILE							= xbmcvfs.translatePath(os.path.join(dataPath, 'episode_data.json'))
defaultFanart						= os.path.join(addonPath, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addonPath, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
enableBACK						= addon.getSetting('show_homebutton') == 'true'
PLACEMENT						= addon.getSetting('button_place')
BEFORE_AND_AFTER		= addon.getSetting('forward_backward') == 'true'
useThumbAsFanart			= addon.getSetting('use_fanart') == 'true'
enableADJUSTMENT			= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_ov20						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 20
KODI_un21						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) <= 20
BASE_URL							= 'https://www.filmstarts.de'

xbmcplugin.setContent(ADDON_HANDLE, 'movies')

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
	header['Pragma'] = 'no-cache'
	header['Accept'] = '*/*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.8,en;q=0.7'
	if REFERRER:
		header['Referer'] = REFERRER
	return header

def getMultiData(MURLS, method='GET', REF=None, fields=None):
	COMBI_NEW = []
	number = len(MURLS)
	def download(pos, extra, link, url, manager):
		response = manager.request(method, url, fields, headers=_header(REF), timeout=5, retries=3)
		if response and response.status in [200, 201, 202]:
			debug_MS(f"(common.getMultiData[1]) === POS : {str(pos)} === REQUESTED URL : {url} === REQUESTED HEADER : {_header(REF)} ===")
			return [pos, extra, link, url, py3_dec(response.data)]
		else:
			failing(f"(common.getMultiData[1]) ERROR - RESPONSE - ERROR ##### POS : {str(pos)} === STATUS : {str(response.status)} === URL : {url} === DATA : {str(response.data)} #####")
			return [pos, extra, link, url, None]
	with ThreadPoolExecutor() as executor:
		connector = urllib3.PoolManager(maxsize=20, block=True)
		debug_MS("* * * * * * * * * * * * * * * * * * * * * * *")
		picker = [executor.submit(download, pos, extra, link, url, connector) for pos, extra, link, url in MURLS]
		wait(picker, timeout=30, return_when=ALL_COMPLETED)
		for ii, future in enumerate(as_completed(picker), 1):
			try:
				COMBI_NEW.append(future.result())
			except Exception as e:
				failing(f"(common.getMultiData[2]) ERROR - EXEPTION - ERROR ##### FUTURE_CONNECT : {future.result()} === FAILURE : {str(e)} #####")
				dialog.notification(translation(30521).format('DETAILS'), translation(30523).format(str(e)), icon, 10000)
				executor.shutdown()
		if COMBI_NEW:
			matching = [flop for flop in COMBI_NEW[:] if flop[4] is None]
			if len(matching) == number or len(matching) > 5:
				dialog.notification(translation(30521).format('DETAILS'), translation(30524), icon, 10000)
		return COMBI_NEW

def getUrl(url, method='GET', REF=None, headers=None, cookies=None, allow_redirects=True, verify=False, stream=None, data=None, json=None):
	simple = requests.Session()
	ANSWER = None
	try:
		response = simple.get(url, headers=_header(REF), cookies=cookies, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=30)
		ANSWER = response.json() if method in ['GET', 'POST'] else response.text if method == 'LOAD' else response
		debug_MS(f"(common.getUrl) === CALLBACK === STATUS : {str(response.status_code)} || URL : {response.url} || HEADER : {_header(REF)} ===")
	except requests.exceptions.RequestException as e:
		failing(f"(common.getUrl) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(str(e)), icon, 12000)
		return sys.exit(0)
	return ANSWER

def get_Time(info):
	try:
		secs = info
		if not str(info).isdigit():
			info = re.sub('[a-zA-Z]', '', info)
			secs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(info.split(':'))))
		return secs
	except: return None

def cleaning(text):
	if text is not None:
		for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&nbsp;', ' '), ("&quot;", "\""), ("&Quot;", "\""), ('&reg;', ''), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('–', '-'), ('&hellip;', '...'), ('&sup2;', '²'),
					('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'),
					('&Auml;', 'Ä'), ('Ä', 'Ä'), ('&auml;', 'ä'), ('ä', 'ä'), ('&Euml;', 'Ë'), ('&euml;', 'ë'), ('&Iuml;', 'Ï'), ('&iuml;', 'ï'), ('&Ouml;', 'Ö'), ('Ö', 'Ö'), ('&ouml;', 'ö'), ('ö', 'ö'), ('&Uuml;', 'Ü'), ('Ü', 'Ü'), ('&uuml;', 'ü'), ('ü', 'ü'), ('&yuml;', 'ÿ'),
					('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'),
					('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'ó'), ('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
					('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'),
					('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'),
					('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
					('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'),
					("\\'", "'"), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&rsquo;', '’'), ('&lsquo;', '‘'), ('&sbquo;', '’'), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
					('&#9;', ''), ("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#196;', 'Ä'), ('&#214;', 'Ö'), ('&#220;', 'Ü'), ('&#228;', 'ä'), ('&#246;', 'ö'), ('&#252;', 'ü'), ('&#223;', 'ß'), ('&#160;', ' '),
					('&#192;', 'À'), ('&#193;', 'Á'), ('&#194;', 'Â'), ('&#195;', 'Ã'), ('&#197;', 'Å'), ('&#199;', 'Ç'), ('&#200;', 'È'), ('&#201;', 'É'), ('&#202;', 'Ê'),
					('&#203;', 'Ë'), ('&#204;', 'Ì'), ('&#205;', 'Í'), ('&#206;', 'Î'), ('&#207;', 'Ï'), ('&#209;', 'Ñ'), ('&#210;', 'Ò'), ('&#211;', 'Ó'), ('&#212;', 'Ô'),
					('&#213;', 'Õ'), ('&#215;', '×'), ('&#216;', 'Ø'), ('&#217;', 'Ù'), ('&#218;', 'Ú'), ('&#219;', 'Û'), ('&#221;', 'Ý'), ('&#222;', 'Þ'), ('&#224;', 'à'),
					('&#225;', 'á'), ('&#226;', 'â'), ('&#227;', 'ã'), ('&#229;', 'å'), ('&#231;', 'ç'), ('&#232;', 'è'), ('&#233;', 'é'), ('&#234;', 'ê'), ('&#235;', 'ë'),
					('&#236;', 'ì'), ('&#237;', 'í'), ('&#238;', 'î'), ('&#239;', 'ï'), ('&#240;', 'ð'), ('&#241;', 'ñ'), ('&#242;', 'ò'), ('&#243;', 'ó'), ('&#244;', 'ô'),
					('&#245;', 'õ'), ('&#247;', '÷'), ('&#248;', 'ø'), ('&#249;', 'ù'), ('&#250;', 'ú'), ('&#251;', 'û'), ('&#253;', 'ý'), ('&#254;', 'þ'), ('&#255;', 'ÿ'), ('&#287;', 'ğ'),
					('&#304;', 'İ'), ('&#305;', 'ı'), ('&#350;', 'Ş'), ('&#351;', 'ş'), ('&#352;', 'Š'), ('&#353;', 'š'), ('&#376;', 'Ÿ'), ('&#402;', 'ƒ'),
					('&#8211;', '–'), ('&#8212;', '—'), ('&#8226;', '•'), ('&#8230;', '…'), ('&#8240;', '‰'), ('&#8364;', '€'), ('&#8482;', '™'), ('&#169;', '©'), ('&#174;', '®'), ('&#183;', '·')):
					text = text.replace(*n)
		text = text.strip()
	return text

def enlargeIMG(cover):
	debug_MS("(common.enlargeIMG) -------------------------------------------------- START = enlargeIMG --------------------------------------------------")
	debug_MS(f"(common.enlargeIMG) ### 1.Original-COVER : {cover} ###")
	imgCode = ['commons/', 'medias', 'pictures', 'seriesposter', 'videothumbnails']
	for XL in imgCode:
		if XL in cover:
			try: cover = f"{cover.split('.net/')[0]}.net/{XL}{cover.split(XL)[1]}"
			except: pass
	debug_MS(f"(common.enlargeIMG) ### 2.Converted-COVER : {cover} ###")
	return cover

def convert64(url, nom='utf-8', ign='ignore'):
	debug_MS("(common.convert64) -------------------------------------------------- START = convert64 --------------------------------------------------")
	debug_MS(f"(common.convert64) ### 1.Original-URL : {url} ###")
	b64_string = url.replace('ACr', '')
	b64_string += "=" * ((4 - len(b64_string) % 4) % 4) # FIX for = TypeError: Incorrect padding
	result = base64.b64decode(b64_string).decode(nom, ign)
	debug_MS(f"(common.convert64) ### 2.Converted-URL : {result} ###")
	return result

def decodeURL(url):
	debug_MS("(common.decodeURL) -------------------------------------------------- START = decodeURL --------------------------------------------------")
	debug_MS(f"(common.decodeURL) ### 1.Original-URL : {url} ###")
	normalstring = ['3F', '2D', '13', '1E', '19', '1F', '20', '2A', '21', '22', '2B', '23', '24', '2C', '25', '26', 'BA', 'B1', 'B2', 'BB', 'B3', 'B4', 'BC', 'B5', 'B6', 'BD', 'B7', 'B8', 'BE', 'B9', 'BF', '30', '31', '32', '3B', '33', '34', '3C', '35', '3D', '4A', '41', '42', '4B', '43', '44', '4C', '45', '46', '4D', '47', '48', '4E', '49', '4F', 'C0', 'C1', 'C2', 'CB', 'C3', 'C4', 'CC', 'C5', 'C6', 'CD']
	decodestring = ['_', ':', '%', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	result = ""
	for i in range(0, len(url), 2):
		signs = url[i:i+2]
		ind = normalstring.index(signs)
		result += decodestring[ind]
	debug_MS(f"(common.decodeURL) ### 2.Decoded-URL : {result} ###")
	return result

params = dict(parse_qsl(sys.argv[2][1:]))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
page = unquote_plus(params.get('page', '1'))
position = unquote_plus(params.get('position', '0'))
target = unquote_plus(params.get('target', 'standard'))
extras = unquote_plus(params.get('extras', 'standard'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
