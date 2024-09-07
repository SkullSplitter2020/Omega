# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import PY2

from resources.lib.content import Content
from resources.lib.common import Common
from resources.lib.credential import Credential

import xbmcaddon

if PY2:
    from urlparse import parse_qsl as urllib_parse_qsl
else:
    from urllib.parse import parse_qsl as urllib_parse_qsl


def run(argv):
    plugin = Common(
        addon=xbmcaddon.Addon(),
        addon_handle=int(argv[1])
    )
    credential = Credential(plugin)
    content = Content(plugin, credential)

    params = dict(urllib_parse_qsl(argv[2][1:]))
    if 'action' in params:

        plugin.log('params = {0}'.format(params))

        if params.get('action') == 'listHome':
            content.listHome()
        elif params.get('action') == 'listSubnavi':
            content.listSubnavi(params.get('path'), params.get('hasitems'), params.get('items_to_add'))
        elif params.get('action') == 'showVideos':
            content.showVideos(params.get('path'), params.get('section'), params.get('show_videos'))
        elif params.get('action') == 'showMoreVideos':
            content.showMoreVideos(params.get('path'), int(params.get('page')), params.get('moreLabel'))
        elif params.get('action') == 'playVoD':
            content.playVoD(params.get('path'))
        elif params.get('action') == 'login':
            content.login()
        elif params.get('action') == 'logout':
            content.logout()
        elif params.get('action') == 'clearCache':
            content.clearCache()
    else:
        content.rootDir()
