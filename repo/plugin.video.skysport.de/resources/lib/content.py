# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import PY2

from base64 import b64decode
from bs4 import BeautifulSoup, element as bs4_element, Tag as bs4_tag
from datetime import datetime
from json import load as json_load, loads as json_loads
from re import compile as re_compile, search as re_search
from requests import get as requests_get, post as requests_post, session as requests_session

import xbmcplugin

if PY2:
    from HTMLParser import HTMLParser
    from urlparse import urljoin as urllib_urljoin
    from xbmc import translatePath as xbmcvfs_translatePath
else:
    from html.parser import unescape as htmlparser_unescape
    from urllib.parse import urljoin as urllib_urljoin
    from xbmcvfs import translatePath as xbmcvfs_translatePath


class Content:


    def __init__(self, plugin, credential):
        self.plugin = plugin
        self.credential = credential

        self.base_url = 'https://sport.sky.de'
        self.htmlparser_unescape = HTMLParser().unescape if PY2 else htmlparser_unescape
        self.nav_json = json_load(open(xbmcvfs_translatePath('{0}/resources/navigation.json'.format(self.plugin.addon_path))))
        self.sky_sport_news_icon = '{0}/resources/skysport_news.jpg'.format(xbmcvfs_translatePath(self.plugin.addon_path))
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'


    def rootDir(self):
        url = self.plugin.build_url({'action': 'listHome'})
        self.addDir('Home', url)

        for item in self.nav_json:
            action = item.get('action', 'showVideos')
            if action == 'showVideos':
                url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'show_videos': 'false'})
            else:
                url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'hasitems': 'true' if item.get('children', None) is not None else 'false'})

            self.addDir(item.get('label'), url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def addDir(self, label, url, icon=None):
        self.addVideo(label, url, icon, True)


    def addVideo(self, label, url, icon, isFolder=False):
        li = self.plugin.get_listitem()
        li.setLabel(label)
        li.setArt({'icon': icon, 'thumb': icon})
        li = self.plugin.set_videoinfo(li, dict())
        li.setProperty('IsPlayable', str(isFolder))

        xbmcplugin.addDirectoryItem(handle=self.plugin.addon_handle, url=url, listitem=li, isFolder=isFolder)


    def listHome(self):
        html = requests_get(self.base_url).text
        soup = BeautifulSoup(html, 'html.parser')

        for item in soup('div', 'sdc-site-tile--has-link'):
            videoitem = item.find('span', {'class': 'sdc-site-tile__badge'})
            if videoitem is not None and videoitem.find('path') is not None:
                headline = item.find('h3', {'class': 'sdc-site-tile__headline'})
                label = headline.span.string
                url = self.plugin.build_url({'action': 'playVoD', 'path': headline.a.get('href')})
                icon = item.img.get('src')
                self.addVideo(label, url, icon)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def listSubnavi(self, path, hasitems, items_to_add=None):
        if hasitems == 'false':
            url = urllib_urljoin(self.base_url, path)
            html = requests_get(url).text
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup('a', 'sdc-site-directory__content'):
                if items_to_add and item.get('href') not in items_to_add:
                    continue

                label = item.span.string
                url = self.plugin.build_url({'action': 'showVideos', 'path': '{0}-videos'.format(item.get('href')), 'show_videos': 'false'})
                self.addDir(label, url)
        else:
            items = None
            for nav_item in self.nav_json:
                if nav_item.get('path') == path:
                    items = nav_item.get('children')

            if items:
                for item in items:
                    action = item.get('action') if item.get('action', None) else 'showVideos'
                    if action == 'listSubnavi':
                        url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'hasitems': 'true' if item.get('children', None) else 'false', 'items_to_add': item.get('includes')})
                    else:
                        url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'show_videos': 'true' if item.get('show_videos', None) is None or item.get('show_videos') == 'true' else 'false'})
                    self.addDir(item.get('label'), url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def showVideos(self, path, section, show_videos):
        url = urllib_urljoin(self.base_url, path)
        html = requests_get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        if show_videos == 'false':
            containers = soup.findAll('section', {'class': 'sdc-site-carousel--sports-rail'})
            if containers is not None:
                for c in containers:
                    if isinstance(c, bs4_tag):
                        label = c.find('h2', {'class', 'sdc-site-carousel__title'}).string
                        all_tag = c.find('span', {'class': 'sdc-site-carousel__view-all'})
                        if all_tag:
                            url = self.plugin.build_url({'action': 'showVideos', 'path': all_tag.a.get('href'), 'show_videos': 'true'})
                        else:
                            url = self.plugin.build_url({'action': 'showVideos', 'path': path, 'show_videos': 'true', 'section': label})
                        if label is not None and label != '' and url:
                            self.addDir(label, url)
        else:
            self.addVideos(soup, section)
            load_more = soup.find('div', {'class': 'sdc-site-load-more'})
            if load_more:
                label = load_more.get('data-button-label')
                path = json_loads(load_more.get('data-ajax-config')).get('url')
                url = self.plugin.build_url({'action': 'showMoreVideos', 'path': path, 'page': 1, 'moreLabel': label})
                self.addDir(label, url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def addVideos(self, soup, section):
        if section:
            soup = soup.find('section', {'title': section})
        for item in soup.find_all('div', class_=re_compile('^sdc-site-tile--has-link')):
            link = item.find('a', {'class': 'sdc-site-tile__headline-link'})
            label = link.span.string
            url = self.plugin.build_url({'action': 'playVoD', 'path': link.get('href')})
            icon = item.img.get('src')
            self.addVideo(label, url, icon)


    def showMoreVideos(self, path, page, moreLabel):
        page += 1
        url = urllib_urljoin(self.base_url, path).replace('${page}', str(page))
        res = requests_get(url)

        if res.status_code == 200:
            res_json = res.json()
            items = res_json.get('items')
            self.addVideos(BeautifulSoup(items, 'html.parser'), None)
            if res_json.get('itemsReturned') == int(res_json.get('perPage')):
                url = self.plugin.build_url({'action': 'showMoreVideos', 'path': path, 'page': page, 'moreLabel': moreLabel})
                self.addDir(moreLabel, url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def getVideoConfigFromCache(self, path):
        return self.plugin.cache.cacheFunction(self.getVideoConfig, path)


    def getVideoConfig(self, path):
        video_config = dict()

        url = urllib_urljoin(self.base_url, path)
        html = requests_get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        div = soup.find('div', {'class': 'sdc-site-video'})
        if div:
            video_config.update(dict(
                                    account_id=div.get('data-account-id'),
                                    id=div.get('data-sdc-video-id'),
                                    auth_config=json_loads(div.get('data-auth-config')),
                                    originator_handle=div.get('data-originator-handle'),
                                    package_name=div.get('data-package-name')
                                    ))

        if not video_config:
            scripts = soup.findAll('script')
            for script in scripts:
                if hasattr(bs4_element, 'Script') and isinstance(script.string, bs4_element.Script):
                    script = script.string
                else:
                    script = script.text

                match = re_search('data-account-id="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(account_id=match.group(1)))

                match = re_search('data-sdc-video-id="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(id=match.group(1)))

                match = re_search('data-auth-config="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(auth_config=json_loads(self.htmlparser_unescape(match.group(1)))))

                match = re_search('data-originator-handle="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(originator_handle=match.group(1)))

                match = re_search('data-package-name="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(package_name=match.group(1)))

                video_config.update(dict(user_token_required=True))

        return video_config


    def playVoD(self, path):
        video_config = self.getVideoConfigFromCache(path)
        if video_config:
            li = self.getVideoListItem(video_config)
        else:
            li = self.plugin.get_listitem()
        xbmcplugin.setResolvedUrl(self.plugin.addon_handle, True, li)


    def getVideoListItem(self, video_config):
        li = self.plugin.get_listitem()

        cookie_jar = self.credential.load_cookies()
        at_cookies = [cookie for cookie in cookie_jar if cookie.name == 'accessToken']
        rt_cookies = [cookie for cookie in cookie_jar if cookie.name == 'refreshToken']
        if rt_cookies and (not at_cookies or (at_cookies and datetime.fromtimestamp(int(at_cookies[0].expires)) < datetime.now())):
            self.refreshCookies(cookie_jar)

        video_config = self.getVideoToken(video_config, cookie_jar)
        if video_config.get('user_token_required') and not at_cookies:
            self.plugin.dialog_notification('Login erforderlich')
        elif not video_config.get('token'):
            self.plugin.dialog_notification('Auth-Token konnte nicht abgerufen werden')
        else:
            url = self.getUrl(video_config)
            li.setPath('{0}|{1}'.format(url, self.user_agent))

        return li


    def getUrl(self, video_config):
        url = 'https://edge-auth.api.brightcove.com/playback/v1/accounts/{0}/videos/ref%3A{1}'.format(video_config.get('account_id'), video_config.get('id'))
        res = requests_get(url, headers=dict(Authorization='Bearer {0}'.format(video_config.get('token'))))
        video = dict()
        for source in res.json().get('sources'):
            if not source.get('width'):
                continue
            if not video or video.get('width') < source.get('width'):
                video = source
        return video.get('src')


    def getVideoToken(self, video_config, cookie_jar):
        headers = video_config.get('auth_config').get('headers')
        data = dict(fileReference=video_config.get('id'), v='2', originatorHandle=video_config.get('originator_handle'))
        res = requests_post('{0}{1}'.format(self.base_url, video_config.get('auth_config').get('url')), headers=headers, cookies=cookie_jar, data=data)
        if res.status_code == 200:
            video_config.update(dict(token=res.text[1:-1]))
        return video_config


    def refreshCookies(self, cookie_jar):
        res = requests_get('{0}/getEntitlements'.format(self.base_url), cookies=cookie_jar)
        if res.status_code == 200:
            for cookie in res.cookies:
                cookie_jar.set_cookie(cookie)
            cookie_jar.save()


    def login(self, silence=False):

        _session = requests_session()
        cookie_jar = self.credential.load_cookies()
        _session.cookie = cookie_jar

        res = _session.get('{0}/login'.format(self.base_url))
        request_url = res.url

        res = _session.get(request_url)
        request_url = res.url

        csrf = None
        match = re_search('<input.*?name="_csrf"\s+?value="(.*?)"', res.text)
        if match:
            csrf = match.group(1)

        js_url = None
        match = re_search('\s<script\s+?type="text\/javascript"\s+src="(.*?)"><\/script>', res.text)
        if match:
            js_url = match.group(1)

        # TO-DO: determine sensor_data
        sensor_data = ''
        res = _session.post('https://id.sport.sky.de{0}'.format(js_url), data=sensor_data)
        request_url = res.url

        user_data = self.credential.get_credentials()
        signin_data = dict(username=user_data.get('user'), password=user_data.get('password'), _csrf=csrf, sessCounter=_session.cookies.get_dict().get('sessionCounter'))
        res = _session.post('https://id.sport.sky.de/site/signin', data=signin_data, allow_redirects=False)
        request_url = res.headers.get('location')
        if res.status_code != 302:
            self.plugin.log('res text = {0}'.format(res.text))
            self.plugin.dialog_notification('Anmeldung nicht erfolgreich')
        else:
            res = _session.get(request_url)
            request_url = res.url

            for cookie in _session.cookies:
                cookie_jar.set_cookie(cookie)
            cookie_jar.save()

            if silence == False:
                if self.credential.has_credentials == False:
                    self.credential.set_credentials(user_data.get('user'), user_data.get('password'))
                self.plugin.dialog_notification('Anmeldung erfolgreich')


    def logout(self):
        self.credential.clear_credentials()
        self.plugin.set_setting('login_acc', '')
        self.plugin.set_setting('booked_packages', '')
        self.plugin.dialog_notification('Abmeldung erfolgreich')


    def clearCache(self):
        self.plugin.cache.delete('%')
        self.plugin.dialog_notification('Leeren des Caches erfolgreich')
