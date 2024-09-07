import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

import sys
from urllib.parse import parse_qsl, urlencode
import os

addon = xbmcaddon.Addon()
addonpath = addon.getAddonInfo('path')
player = xbmc.Player()

streams = dict({'1.Radio BOB Live': ['http://psr.hoerradar.de/psr-live-mp3-hq', 'Radio Bob.jpg'],
                '2.Hardrock': ['http://bob.hoerradar.de/radiobob-hardrock-mp3-hq?sABC=594pp098%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202264', 'Hard Rock Music.jpg'],
                '3.Rockhits': ['http://bob.hoerradar.de/radiobob-rockhits-mp3-hq?sABC=594pos49%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498201929', 'Rockhits.jpg'],
                '4.Best of Rock': ['http://bob.hoerradar.de/radiobob-bestofrock-mp3-hq?sABC=594pp035%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202165', 'Best of Rock.jpg'],
                '5.80er Rock': ['http://bob.hoerradar.de/radiobob-80srock-mp3-hq?sABC=594pos91%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202001', '80er.jpg'],
                '6.90er Rock': ['http://bob.hoerradar.de/radiobob-90srock-mp3-hq?sABC=594posns%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202031', '90er.jpg'],
                '7.AC/DC': ['http://bob.hoerradar.de/radiobob-acdc-mp3-hq?sABC=594porqq%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498201821', 'ACDC.jpg'],
                '8.Queen': ['http://bob.hoerradar.de/radiobob-queen-mp3-hq?sABC=594pp1sp%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202620', 'RadioQueen.jpg'],
                '9.Classic Rock': ['http://webradio.antennevorarlberg.at/classicrock', 'Classic Rock.jpg'],
                '10.Rockradio': ['http://webradio.antennevorarlberg.at/rock', 'Rock Radio.jpg'],
                '11.Rt1-Rock': ['http://rt1-ais-edge-4004-dus-dtag-cdn.cast.addradio.de/rt1/rock/mp3/high/stream.mp3?_art=dj0yJmlwPTM3LjE0OC4xNTUuODAmaWQ9aWNzY3hsLWdlZGU2c3lqYiZ0PTE2MTUwNDMwNDgmcz03ODY2ZjI5YyM4MmRhY2ZmMmIyY2UwOWYzMDE3NmI5NTljODJkMjk5OA', 'Rt1 Rock.jpg'],
                '12.Rockfeuer': ['https://rockfeuer.stream.laut.fm/rockfeuer?pl=m3u&t302=2018-08-08_21-18-58&uuid=166bb044-9139-4021-b1cc-6aeafe6826ca', 'Rockfeuer.jpg'],
                '13.Wackenradio BOB': ['http://bob.hoerradar.de/radiobob-wacken-mp3-hq?sABC=594pp009%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202121', 'wacken-bob.jpg'],
                '14.Wackenradio': ['http://de-hz-fal-stream02.rautemusik.fm/wackenradio?listenerid=e862a9579a1f3f248baba2f5bdfcbe39', 'Wacken.jpg'],
                '15.Punk Rock': ['http://bob.hoerradar.de/radiobob-punk-mp3-hq?sABC=594pp183%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202499', 'Punk Rock.jpg'],
                '16.Deutschrock': ['http://bob.hoerradar.de/radiobob-deutschrock-mp3-hq?sABC=594pos2o%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498201899', 'Deutschrock.jpg'],
                '17.110 Prozent-Deutschrock.de': ['http://server19350.streamplus.de/;stream.mp3', '110-AP-Radio.jpg'],
                '17.Germanyrock': ['https://germanyrock.stream.laut.fm/germanyrock?t302=2017-11-15_09-20-22&uuid=4153a3c5-b8d0-42ec-868d-2d2a3a78839d', 'Germanrock.jpg'],
                '19.Kuschel Rock': ['http://bob.hoerradar.de/radiobob-kuschelrock-mp3-hq?sABC=594pp1r0%230%2314rn0443777qq2150q92366o63q207nn%23ubzrcntr&amsparams=playerid:homepage;skey:1498202592', 'stream-tile-rock.jpg']})


def get_url(params):
    return '{0}?{1}'.format(_url, urlencode(params))


def get_image(image):
    return os.path.join(addonpath, 'resources', 'images', image)


def list_streams():
    xbmcplugin.setPluginCategory(_handle, 'Stube Gok  Streams')
    xbmcplugin.setContent(_handle, 'songs')

    for stream in streams:
        liz = xbmcgui.ListItem(label=stream)
        liz.setPath(streams[stream][0])
        liz.setArt({'icon': get_image(streams[stream][1]), 'fanart': get_image('fanart.jpg')})
        liz.setProperty('IsPlayable', 'true')
        url = get_url({'action': 'play', 'url': streams[stream][0],
                       'icon': get_image(streams[stream][1]),
                       'title': 'Stube Gok Radio \'{}\' Stream'.format(stream)})
        xbmcplugin.addDirectoryItem(_handle, url, liz, isFolder=False)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_stream(path, icon, title):
    if player.isPlaying():
        xbmc.log('Stop player')
        player.stop()
    xbmc.log('Playing {}'.format(path))
    play_item = xbmcgui.ListItem(path=path)
    play_item.setInfo('music', {'title': title})
    play_item.setArt({'icon': icon, 'thumb': icon, 'fanart': get_image('fanart.jpg')})
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(route):
    params = dict(parse_qsl(route))
    xbmc.log('Parameter list: {}'.format(params), xbmc.LOGDEBUG)
    if params:
        if params['action'] == 'play':
            play_stream(params['url'], params['icon'], params['title'])
    else:
        list_streams()


_url = sys.argv[0]
_handle = int(sys.argv[1])

if __name__ == '__main__':
    try:
        router(sys.argv[2][1:])
    except IndexError:
        pass
