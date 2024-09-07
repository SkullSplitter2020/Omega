# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import PY2, py2_encode

from base64 import b64encode as base64_b64encode, b64decode as base64_b64decode
from hashlib import md5 as hashlib_md5
from time import sleep as time_sleep
from uuid import UUID as uuid_UUID, uuid1 as uuid_uuid1

import xbmc
import xbmcgui

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

if PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode


class Common:


    def __init__(self, addon=None, addon_handle=None):
        self.addon = addon
        self.addon_handle = addon_handle
        self.addon_id = self.addon.getAddonInfo('id')
        self.addon_name = self.addon.getAddonInfo('name')
        self.addon_path = self.addon.getAddonInfo('path')
        self.addon_profile = self.addon.getAddonInfo('profile')
        self.kodi_version = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

        self.cache = StorageServer.StorageServer(py2_encode('{0}.videoid').format(self.addon_name), 24 * 30)


    def log(self, msg):
        xbmc.log(str(msg), xbmc.LOGDEBUG)


    def build_url(self, query):
        return 'plugin://{0}?{1}'.format(self.addon_id, urlencode(query))


    def b64enc(self, data):
        enc_data = base64_b64encode(data)
        missing_padding = len(enc_data) % 4
        if missing_padding != 0:
            enc_data = '{0}{1}'.format(enc_data, py2_encode('=') * (4 - missing_padding))
        return enc_data


    def b64dec(self, data):
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data = '{0}{1}'.format(data, py2_encode('=') * (4 - missing_padding))
        return base64_b64decode(data)


    def get_listitem(self):
        return xbmcgui.ListItem()


    def get_dialog(self):
        return xbmcgui.Dialog()


    def dialog_ok(self, msg):
        self.get_dialog().ok(self.addon_name, msg)


    def dialog_notification(self, msg, icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=True):
        self.get_dialog().notification(self.addon_name, msg, icon, time, sound)


    def set_setting(self, key, value):
        return self.addon.setSetting(key, value)


    def get_setting(self, key):
        return self.addon.getSetting(key)


    def uniq_id(self):
        device_id = ''
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        # hack response busy
        i = 0
        while not py2_encode(':') in mac_addr and i < 3:
            i += 1
            time_sleep(1)
            mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        if py2_encode(':') in mac_addr:
            device_id = str(uuid_UUID(hashlib_md5(mac_addr.encode('utf-8')).hexdigest()))
        elif xbmc.getCondVisibility('System.Platform.Android'):
            device_id = str(uuid_UUID(hashlib_md5(self.get_android_uuid().encode('utf-8')).hexdigest()))

        if device_id == '':
            self.log('[{0}] error: failed to get device id ({1})'.format(self.addon_id, str(mac_addr)))
            self.dialog_ok('Geräte-Id konnte nicht ermittelt werden.')

        return device_id


    def get_android_uuid(self):
        from subprocess import PIPE as subprocess_PIPE, Popen as subprocess_Popen
        from re import sub as re_sub
        values = ''
        try:
            # Due to the new android security we cannot get any type of serials
            sys_prop = ['ro.product.board', 'ro.product.brand', 'ro.product.device', 'ro.product.locale'
                        'ro.product.manufacturer', 'ro.product.model', 'ro.product.platform',
                        'persist.sys.timezone', 'persist.sys.locale', 'net.hostname']
            # Warning net.hostname property starting from android 10 is deprecated return empty
            with subprocess_Popen(['/system/bin/getprop'], stdout=subprocess_PIPE) as proc:
                output_data = proc.communicate()[0].decode('utf-8')
            list_values = output_data.splitlines()
            for value in list_values:
                value_splitted = re_sub(r'\[|\]|\s', '', value).split(':')
                if value_splitted[0] in sys_prop:
                    values += value_splitted[1]
        except Exception:
            pass
        return values


    def set_videoinfo(self, listitem, infolabels):

        if self.kodi_version < 20:
            listitem.getVideoInfoTag()
        else:
            listitem.setInfo('video', infolabels)

        return listitem
