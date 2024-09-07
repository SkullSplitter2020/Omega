import xbmcaddon

import os

#########################################################
#         Global Variables - DON'T EDIT!!!              #
#########################################################
ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PATH = xbmcaddon.Addon().getAddonInfo('path')
ART = os.path.join(PATH, 'resources', 'media')
#########################################################

#########################################################
#        User Edit Variables                            #
#########################################################
ADDONTITLE = '[B][COLOR indianred]sKulls[/COLOR] [COLOR gold]Fusion[/COLOR] [COLOR indianred]Wizard[/COLOR][/B]'
BUILDERNAME = '[COLOR indianred]sKulls[/COLOR] [COLOR gold]Fusion[/COLOR] [COLOR indianred]Wizard[/COLOR]'
EXCLUDES = [ADDON_ID, 'repository.skulls']
# Text File with build info in it. 
BUILDFILE = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/txt/builds.txt'
# How often you would like it to check for build updates in days
# 0 being every startup of kodi
UPDATECHECK = 0
# Text File with apk info in it.  Leave as 'http://' to ignore
APKFILE = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/txt/apk.txt'
# Text File with Youtube Videos urls.  Leave as 'http://' to ignore
YOUTUBETITLE = 'http://'
YOUTUBEFILE = 'http://'
# Text File for addon installer.  Leave as 'http://' to ignore
ADDONFILE = 'http://'
# Text File for advanced settings.  Leave as 'http://' to ignore
ADVANCEDFILE = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/advsettings/advsettings.json'
#########################################################

#########################################################
#        Theming Menu Items                             #
#########################################################
# If you want to use locally stored icons the place them in the Resources/Art/
# folder of the wizard then use os.path.join(ART, 'imagename.png')
# do not place quotes around os.path.join
# Example:  ICONMAINT     = os.path.join(ART, 'mainticon.png')
#           ICONSETTINGS  = 'https://www.yourhost.com/repo/wizard/settings.png'
# Leave as http:// for default icon
ICONBUILDS = os.path.join(ART, 'builds.png')
ICONMAINT = os.path.join(ART, 'maintenance.png')
ICONSPEED = os.path.join(ART, 'speed.png')
ICONAPK = os.path.join(ART, 'apkinstaller.png')
ICONADDONS = os.path.join(ART, 'addoninstaller.png')
ICONYOUTUBE = os.path.join(ART, 'youtube.png')
ICONSAVE = os.path.join(ART, 'savedata.png')
ICONTRAKT = os.path.join(ART, 'keeptrakt.png')
ICONREAL = os.path.join(ART, 'keepdebrid.png')
ICONLOGIN = os.path.join(ART, 'keeplogin.png')
ICONCONTACT = os.path.join(ART, 'information.png')
ICONSETTINGS = os.path.join(ART, 'settings.png')
# Hide the section separators 'Yes' or 'No'
HIDESPACERS = 'No'
# Character used in separator
SPACER = '='

# You can edit these however you want, just make sure that you have a %s in each of the
# THEME's so it grabs the text from the menu item
COLOR1 = 'indianred'
COLOR2 = 'white'
# COLOR3 = 'red'
COLOR3 = 'gold'
# Primary menu items   / {0} is the menu item and is required
THEME1 = u'[COLOR {color1}][COLOR {color1}][B] - [/B][/COLOR][COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2, color3=COLOR3)
# Build Names          / {0} is the menu item and is required
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR3)
# Alternate items      / {0} is the menu item and is required
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
# Current Build Header / {0} is the menu item and is required
THEME4 = u'[COLOR {color1}]Current Build:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# Current Theme Header / {0} is the menu item and is required
THEME5 = u'[COLOR {color1}]Current Theme:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)


# Message for Contact Page
# Enable 'Contact' menu item 'Yes' hide or 'No' dont hide
HIDECONTACT = 'No'
# You can add \n to do line breaks
CONTACT = ' Vielen Dank, dass Sie sich für das\n\n [COLOR indianred]sKulls[/COLOR] [COLOR gold]Fusion[/COLOR] [COLOR indianred]Build[/COLOR]\n\n entschieden haben.\n\n Kontakt per Telegram [COLOR white]>https://t.me/sKulls_inc[/COLOR]'
# Images used for the contact window.  http:// for default icon and fanart
CONTACTICON = os.path.join(ART, 'qricon.png')
CONTACTFANART = 'http://'
#########################################################

#########################################################
#        Auto Update For Those With No Repo             #
#########################################################
# Enable Auto Update 'Yes' or 'No'
AUTOUPDATE = 'Yes'
# Url to wizard version
WIZARDFILE = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/repo/zips/plugin.program.sKullswizard' 
#########################################################

#########################################################
#        Auto Install Repo If Not Installed             #
#########################################################
# Enable Auto Install 'Yes' or 'No'
AUTOINSTALL = 'No'
# Addon ID for the repository
REPOID = 'repository.skulls'
# Url to Addons.xml file in your repo folder(this is so we can get the latest version)
REPOADDONXML = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/repo/zips/addons.xml'
# Url to folder zip is located in
REPOZIPURL = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/repo/zips/repository.skulls/'
#########################################################

#########################################################
#        Notification Window                            #
#########################################################
# Enable Notification screen Yes or No
ENABLE = 'Yes'
# Url to notification file
NOTIFICATION = 'https://skullsplitter.myqnapcloud.com/skullskodibuild/kodi/txt/notify.txt'
# Use either 'Text' or 'Image'
HEADERTYPE = 'Image'
# Font size of header
FONTHEADER = 'Font14'
HEADERMESSAGE = '[B][COLOR indianred]sKulls[/COLOR] [COLOR gold]Fusion[/COLOR] [COLOR indianred]Wizard[/COLOR][/B]'
# url to image if using Image 424x180
HEADERIMAGE = 'https://i.ibb.co/BBpMY28/Banner.png'
# Font for Notification Window
FONTSETTINGS = 'Font13'
# Background for Notification Window
BACKGROUND = 'https://i.ibb.co/2KvFxNx/fanart.png'
#########################################################
