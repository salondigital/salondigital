import zipfile, xbmcaddon, xbmc, sys, os, time, io, struct
import wizard as wiz

ADDON_ID       = xbmcaddon.Addon().getAddonInfo('id')
ADDONTITLE     = 'SalonDigital'
COLOR1         = 'red'
COLOR2         = 'white'
ADDON          = wiz.addonId(ADDON_ID)
HOME           = xbmc.translatePath('special://home/')
USERDATA       = os.path.join(HOME,      'userdata')
GUISETTINGS    = os.path.join(USERDATA,  'guisettings.xml')
KEEPFAVS       = wiz.getS('keepfavourites')
KEEPSOURCES    = wiz.getS('keepsources')
KEEPPROFILES   = wiz.getS('keepprofiles')
KEEPADVANCED   = wiz.getS('keepadvanced')
KEEPSUPER      = wiz.getS('keepsuper')
KEEPREPOS      = wiz.getS('keeprepos')
KEEPWHITELIST  = wiz.getS('keepwhitelist')
KODIV          = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
LOGFILES       = ['xbmc.log', 'xbmc.old.log', 'kodi.log', 'kodi.old.log', 'spmc.log', 'spmc.old.log', 'tvmc.log', 'tvmc.old.log', 'Thumbs.db', '.gitignore', '.DS_Store']
bad_files      = ['onechannelcache.db', 'saltscache.db', 'saltscache.db-shm', 'saltscache.db-wal', 'saltshd.lite.db', 'saltshd.lite.db-shm', 'saltshd.lite.db-wal', 'queue.db', 'commoncache.db', 'access.log', 'trakt.db', 'video_cache.db']

def fixZip(zip):
	with open(zip, 'rb') as f:
		data = f.read()
	i = data.rindex(b'PK\5\6') + 22
	i += struct.unpack('<H', data[i-2: i])[0]
	if data[i:].strip(b'\0') == b'':
		data = data[:i]
	return zipfile.ZipFile(io.BytesIO(data))

def all(_in, _out, dp=None, ignore=None, title=None):
	if dp: return allWithProgress(_in, _out, dp, ignore, title)
	else: return allNoProgress(_in, _out, ignore)

def allNoProgress(_in, _out, ignore, fix=False):
	try:
		if fix:
			zin = fixZip(_in)
		else:
			zin = zipfile.ZipFile(_in, 'r')
		zin.extractall(_out)
	except Exception, e:
		if not fix:
			return allNoProgress(_in, _out, ignore, True)
		else:		
			print str(e)
			return False
	return True

def allWithProgress(_in, _out, dp, ignore, title, fix=False):
	count = 0; errors = 0; error = ''; update = 0; size = 0; excludes = []
	try:
		if fix:
			zin = fixZip(_in)
		else:
			zin = zipfile.ZipFile(_in,  'r')
	except Exception, e:
		if not fix:
			return allWithProgress(_in, _out, dp, ignore, title, True)
		else:
			errors += 1; error += '%s\n' % e
			wiz.log('Error Checking Zip: %s' % str(e), xbmc.LOGERROR)
			return update, errors, error
	
	whitelist = wiz.whiteList('read')
	for item in whitelist:
		try: name, id, fold = item
		except: pass
		excludes.append(fold)
		if fold.startswith('pvr'):
			wiz.setS('pvrclient', id)
	
	nFiles = float(len(zin.namelist()))
	zipsize = wiz.convertSize(sum([item.file_size for item in zin.infolist()]))

	zipit = str(_in).replace('\\', '/').split('/')
	title = title if not title == None else zipit[-1].replace('.zip', '')

	for item in zin.infolist():
		count += 1; prog = int(count / nFiles * 100); size += item.file_size
		file = str(item.filename).split('/')
		skip = False
		line1  = '%s [COLOR %s][B][Errores:%s][/B][/COLOR]' % (title, COLOR2, errors)
		line2  = '[COLOR %s][B]Archivo:[/B][/COLOR] [COLOR %s]%s/%s[/COLOR] ' % (COLOR2, COLOR1, count, int(nFiles))
		line2 += '[COLOR %s][B]Tamano:[/B][/COLOR] [COLOR %s]%s/%s[/COLOR]' % (COLOR2, COLOR1, wiz.convertSize(size), zipsize)
		line3  = '[COLOR %s]%s[/COLOR]' % (COLOR1, item.filename)
		if item.filename == 'userdata/sources.xml' and KEEPSOURCES == 'true': skip = True
		elif item.filename == 'userdata/favourites.xml' and KEEPFAVS == 'true': skip = True
		elif item.filename == 'userdata/profiles.xml' and KEEPPROFILES == 'true': skip = True
		elif item.filename == 'userdata/advancedsettings.xml' and KEEPADVANCED == 'true': skip = True
		elif file[0] == 'addons' and file[1] in excludes: skip = True
		elif file[0] == 'userdata' and file[1] == 'addon_data' and file[2] in excludes: skip = True
		elif file[-1] in LOGFILES: skip = True
		elif file[-1] in bad_files: skip = True
		elif file[-1].endswith('.csv'): skip = True
		elif not str(item.filename).find('plugin.program.super.favourites') == -1 and KEEPSUPER == 'true': skip = True
		elif not str(item.filename).find(ADDON_ID) == -1 and ignore == None: skip = True
		if skip == True: wiz.log("Saltando: %s" % item.filename, xbmc.LOGNOTICE)
		else:
			try:
				zin.extract(item, _out)
			except Exception, e:
				errormsg  = "[COLOR %s]Archivo:[/COLOR] [COLOR %s]%s[/COLOR]\n" % (COLOR2, COLOR1, file[-1])
				errormsg += "[COLOR %s]Carpeta:[/COLOR] [COLOR %s]%s[/COLOR]\n" % (COLOR2, COLOR1, (item.filename).replace(file[-1],''))
				errormsg += "[COLOR %s]Error:[/COLOR] [COLOR %s]%s[/COLOR]\n\n" % (COLOR2, COLOR1, str(e).replace('\\\\','\\').replace("'%s'" % item.filename, ''))
				errors += 1; error += errormsg
				wiz.log('Error Extracting: %s(%s)' % (item.filename, str(e)), xbmc.LOGERROR)
				pass
		dp.update(prog, line1, line2, line3)
		if dp.iscanceled(): break
	if dp.iscanceled(): 
		dp.close()
		wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Extraccion cancelada![/COLOR]" % COLOR2)
		sys.exit()
	return prog, errors, error