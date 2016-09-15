import re;import os;import sys;import time;import ntpath;import base64;import shutil;import zipfile;import hashlib;import platform;import urllib;import urllib2;import xbmc;import xbmcgui;import xbmcaddon;import xbmcplugin

ADDON_NAME   = xbmcaddon.Addon('plugin.video.salondigital.android')

BASE_URL     = 'http://salondigital.es/'
WIZARD_PAGE  = 'wizard.php'
USER_AGENT   = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36 ReplicantWizard/1.0.0'

INSTALL_PAGE = 'http://salondigital.es/check.php'

def unzip(_in, _out, progress):
    __in = zipfile.ZipFile(_in,  'r')

    nofiles = float(len(__in.infolist()))
    count   = 0

    try:
        for item in __in.infolist():
            count += 1
            update = (count / nofiles) * 100

            if progress.iscanceled():
                dialog = xbmcgui.Dialog()
                dialog.ok('Intelligent Installer', 'La descompresion se ha cancelado.')

                sys.exit()
                progress.close()

            progress.update(int(update))
            __in.extract(item, _out)

    except Exception, e:
        return False

    return True

def download(url, destination, progress):
    progress.update(0)
    urllib.urlretrieve(url, destination, lambda numblocks, blocksize, filesize, url=url: hook(numblocks, blocksize, filesize, url, progress))

def hook(numblocks, blocksize, filesize, url, progress):
    try:
        percent = min((numblocks * blocksize * 100) / filesize, 100)
        progress.update(percent)

    except:
        percent = 100
        progress.update(percent)

    if progress.iscanceled():
        dialog = xbmcgui.Dialog()
        dialog.ok('Intelligent Installer', 'La descarga se ha cancelado.')

        sys.exit()
        progress.close()

def suminstall():
    dialog = xbmcgui.Dialog()

    link  = openUrl(INSTALL_PAGE + '?email=' + ADDON_NAME.getSetting('email') + '&pass=' + ADDON_NAME.getSetting('pass')).replace('\n', '').replace('\r', '')
    total = re.compile('install="(\d)"').findall(link)

    try:
                
        if (link != '1'):
            dialog.ok('Error de autentificacion', 'Por favor, registrese en http://salondigital.es/foro/viewtopic.php?f=21&t=344', link)
            sys.exit()
        else:
            pass
    except:
        sys.exit()

def categories():
    link  = openUrl(BASE_URL + WIZARD_PAGE).replace('\n', '').replace('\r', '')
    match = re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)

    for name, url, icon, fanart, desc in match:
        addDir(name, url, 1, icon, fanart, desc)

    setView('movies', 'MAIN')

def openUrl(url):
    request  = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)

    response = urllib2.urlopen(request)
    link = response.read()

    response.close()
    return link

def runAddon(name, url, desc):
    root   = xbmc.translatePath(os.path.join('special://', 'home'))
    dialog = xbmcgui.Dialog()

    progress = xbmcgui.DialogProgress()
    progress.create('Intelligent Installer', 'Descargando...')

    path = xbmc.translatePath(os.path.join('special://home/addons', 'packages'))
    archive = os.path.join(path, 'plugin.program.salondigital.zip')

    try:
        os.remove(archive)
    except:
        pass

    download(url, archive, progress)
    time.sleep(2)

    progress.update(0, 'Descomprimiendo...')

    unzip(archive, root, progress)
    time.sleep(2)

    killXbmc()

def killXbmc():
    dialog = xbmcgui.Dialog()
    #dialog.ok('Intelligent Installer', 'Recuerde reiniciar el equipo tras la actualizacion')

    dialog.ok('Intelligent Installer', 'Actualizacion finalizada, por favor, reinicie el equipo')	
		
    platform = queryPlatform()

    if (platform == 'OSX'):
        try:
            os.system('killall -9 XBMC')
        except:
            pass

        try:
            os.system('killall -9 Kodi')
        except:
            pass
    elif (platform == 'AppleTV'):
        try:
            os.system('killall AppleTV')
        except:
            pass

        try:
            os.system('sudo initctl stop kodi')
        except:
            pass

        try:
            os.system('sudo initctl stop xbmc')
        except:
            pass
    elif (platform == 'Linux'):
        try:
            os.system('killall XBMC')
        except:
            pass

        try:
            os.system('killall Kodi')
        except:
            pass

        try:
            os.system('killall -9 xbmc.bin')
        except:
            pass

        try:
            os.system('killall -9 kodi.bin')
        except:
            pass
    elif (platform == 'Android'):
        try:
            os.system('adb shell am force-stop org.xbmc.kodi')
        except:
            pass

        try:
            os.system('adb shell am force-stop org.kodi')
        except:
            pass

        try:
            os.system('adb shell am force-stop org.xbmc.xbmc')
        except:
            pass

        try:
            os.system('adb shell am force-stop org.xbmc')
        except:
            pass
    elif (platform == 'Windows'):
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except:
            pass

        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except:
            pass
    else:
        dialog.ok('Intelligent Installer', 'Por favor, desconecte el cable de corriente de su dispositivo')

def queryPlatform():
    if (xbmc.getCondVisibility('system.platform.osx')):
        return 'OSX'
    elif (xbmc.getCondVisibility('system.platform.atv2')):
        return 'AppleTV'
    elif (xbmc.getCondVisibility('system.platform.linux')):
        return 'Linux'
    elif (xbmc.getCondVisibility('system.platform.android')):
        return 'Android'
    elif (xbmc.getCondVisibility('system.platform.windows')):
        return 'Windows'
    else:
        return 'Other'

def addDir(name, url, mode, icon, fanart, desc):
    __url = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&icon=" + urllib.quote_plus(icon) + "&fanart=" + urllib.quote_plus(fanart) + "&desc=" + urllib.quote_plus(desc)
    __listitem = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=icon)
    __listitem.setInfo(type='Video', infoLabels={ 'Title': name, 'Plot': desc })
    __listitem.setProperty('Fanart_Image', fanart)
    item = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=__url, listitem=__listitem, isFolder=False)
    return item

def getParams():
    param  = []
    string = sys.argv[2]

    if (len(string) >= 2):
        params = sys.argv[2]
        clean  = params.replace('?', '')

        if (params[len(params) -1] == '/'):
            params = params[0:len(params) -2]

        pairs = clean.split('&')
        param = {}

        for i in range(len(pairs)):
            split = {}
            split = pairs[i].split('=')

            if (len(split) == 2):
                param[split[0]] = split[1]

    return param

url  = None
name = None
mode = None
icon = None
fanart = None
desc = None

params = getParams()

try:
    url  = urllib.unquote_plus(params['url'])
except:
    pass

try:
    name = urllib.unquote_plus(params['name'])
except:
    pass

try:
    mode = int(params['mode'])
except:
    pass

try:
    icon = urllib.unquote_plus(params['icon'])
except:
    pass

try:
    fanart = urllib.unquote_plus(params['fanart'])
except:
    pass

try:
    desc = urllib.unquote_plus(params['desc'])
except:
    pass

def setView(content, viewType):
    if (content):
        xbmcplugin.setContent(int(sys.argv[1]), content)

    if (ADDON_NAME.getSetting('auto-view') == 'true'):
        xbmc.executebuiltin('Container.SetViewMode(%s)' % ADDON_NAME.getSetting(viewType))

if ((mode == None) or (url == None) or len(url) < 1):
    suminstall()
    categories()
elif (mode == 1):
    runAddon(name, url, desc)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
