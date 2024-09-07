#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin,xbmcaddon,xbmcgui,os,sys

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path') #.decode('utf-8')
icons_path = os.path.join(addon_path,'resources','icon')
xbmcplugin.setContent(handle=int(sys.argv[1]), content='songs')
				
def add_item(url,infolabels,image=''):
    listitem = xbmcgui.ListItem(infolabels['title'])
    listitem.setInfo('audio',infolabels)
    listitem.setProperty('IsPlayable','true')
    listitem.setArt({ 'thumb': image , 'icon' :image })
    xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,listitem)

add_item('http://stream01.iloveradio.de/iloveradio1.mp3',{'title':'[COLOR yellow]I Love Radio[/COLOR]'},os.path.join(icons_path,'radio.png'))
add_item('http://stream01.iloveradio.de/iloveradio2.mp3',{'title':'[COLOR aqua]I Love 2 Dance Radio[/COLOR]'},os.path.join(icons_path,'dance.png'))
add_item('http://stream01.iloveradio.de/iloveradio9.mp3',{'title':'[COLOR red]I Love Top 100 Charts[/COLOR]'},os.path.join(icons_path,'100charts.png'))
add_item('http://stream01.iloveradio.de/iloveradio3.mp3',{'title':'[COLOR darkolivegreen]I Love The Battle[/COLOR]'},os.path.join(icons_path,'battle.png'))
add_item('http://stream01.iloveradio.de/iloveradio6.mp3',{'title':'[COLOR greenyellow]I Love #Dreist[/COLOR]'},os.path.join(icons_path,'dreist.png'))
add_item('http://stream01.iloveradio.de/iloveradio13.mp3',{'title':'[COLOR darkslateblue]I Love HIP-HOP TurnUp[/COLOR]'},os.path.join(icons_path,'hip-hop.png'))
add_item('http://stream01.iloveradio.de/iloveradio5.mp3',{'title':'[COLOR darkviolet]I Love MashUp[/COLOR]'},os.path.join(icons_path,'mashup.png'))
add_item('http://stream01.iloveradio.de/iloveradio4.mp3',{'title':'[COLOR lime]I Love BASS[/COLOR]'},os.path.join(icons_path,'bass.png'))
add_item('http://stream01.iloveradio.de/iloveradio12.mp3',{'title':'[COLOR palevioletred]I Love Hits History[/COLOR]'},os.path.join(icons_path,'history.png'))
add_item('http://stream01.iloveradio.de/iloveradio11.mp3',{'title':'[COLOR magenta]I Love Popstars[/COLOR]'},os.path.join(icons_path,'popstars.png'))
add_item('http://stream01.iloveradio.de/iloveradio10.mp3',{'title':'[COLOR orchid]I Love Radio & Chill[/COLOR]'},os.path.join(icons_path,'radio+chill.png'))
add_item('http://stream01.iloveradio.de/iloveradio7.mp3',{'title':'[COLOR goldenrod]I Love About: Berlin[/COLOR]'},os.path.join(icons_path,'berlin.png'))
add_item('http://stream01.iloveradio.de/iloveradio8.mp3',{'title':'[COLOR maroon]I Love X-MAS[/COLOR]'},os.path.join(icons_path,'x-mas.png'))
add_item('http://stream01.iloveradio.de/iloveradio105.mp3',{'title':'[COLOR darkgray]Top 100 Pop[/COLOR]'},os.path.join(icons_path,'100pop.png'))
add_item('http://stream01.iloveradio.de/iloveradio108.mp3',{'title':'[COLOR darkgray]Top 100 Hip-Hop[/COLOR]'},os.path.join(icons_path,'100hip-hop.png'))
add_item('http://stream01.iloveradio.de/iloveradio103.mp3',{'title':'[COLOR darkgray]Top 100 Dance & DJS[/COLOR]'},os.path.join(icons_path,'100dance+djs.png'))
add_item('http://stream04.iloveradio.de/iloveradio9.mp3',{"title":'[COLOR darkorange]I Love Bravo Charts[/COLOR]'},os.path.join(icons_path,'bravo.png'))
add_item('http://streams.bigfm.de/urbanilr-128-mp3',{'title':'[COLOR orange]I Love Urban Club Beats[/COLOR]'},os.path.join(icons_path,'club-beats.png'))
add_item('http://streams.bigfm.de/grooveilr-128-mp3',{'title':'[COLOR orange]I Love Groove Night[/COLOR]'},os.path.join(icons_path,'groovenight.png'))
add_item('http://streams.bigfm.de/nitroxedmilr-128-mp3',{'title':'[COLOR orange]I Love EDM-Progressive[/COLOR]'},os.path.join(icons_path,'edm.png'))
add_item('http://streams.bigfm.de/nitroxdeepilr-128-mp3',{'title':'[COLOR orange]I Love Deep Techhouse[/COLOR]'},os.path.join(icons_path,'techhouse.png'))

if addon.getSetting('sort') == 'true':
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)

xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.getSetting('view-mode'))
xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True, updateListing=False, cacheToDisc=False)