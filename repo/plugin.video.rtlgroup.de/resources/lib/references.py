# -*- coding: utf-8 -*-

from .common import *


class Registration(object):

	def __init__(self):
		self.tempSIGNED_folder = tempSIGNED
		self.signed_file = signedFile
		self.tempFREE_folder = tempFREE
		self.free_file = freeFile
		self.username = addon.getSetting('username')
		self.password = addon.getSetting('password')

	def get_mac_key(self):
		debug_MS("(references.get_mac_key) ### START get_mac_key ###")
		mac = uuid.getnode()
		try: clear_mac = ':'.join(i + j for i, j in zip(hex(mac)[2:].zfill(12)[::2], hex(mac)[2:].zfill(12)[1::2]))
		except: clear_mac = 'ERROR NO -MAC ADRESS- FOUND'
		if (mac >> 40) % 2:
			mac = node()
		return (str(clear_mac), uuid.uuid5(uuid.NAMESPACE_DNS, str(mac)).bytes)

	def specs_encrypt(self, data):
		MAC_CLEAR, MAC_CODE = self.get_mac_key()
		keys = DES3.new(MAC_CODE, DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
		coding = keys.encrypt(pad(data.encode('utf-8'), DES3.block_size))
		return base64.b64encode(coding)

	def specs_decrypt(self, data, course='UNKNOWN'):
		if not data:
			return ""
		force_encrypt = (True if addon.getSetting('encrypted') == 'JA - ENCRYPTED' else False)
		its_base64 = re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$', data)
		if its_base64 and force_encrypt is True:
			debug_MS(f"(references.specs_decrypt[1]) XXX FORCE_ENCRYPT : {str(force_encrypt)} || Base64.Match : {its_base64.groups()} || SUCCESS FOR '{course}' XXX")
			data += "=" * ((4 - len(data) % 4) % 4) # FIX for = TypeError: Incorrect padding
			MAC_CLEAR, MAC_CODE = self.get_mac_key()
			keys = DES3.new(MAC_CODE, DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
			try:
				coding = unpad(keys.decrypt(base64.b64decode(data)), DES3.block_size)
				return coding.decode('utf-8')
			except:
				if course == 'PASSWORD':
					failing("(references.specs_decrypt[2]) XXXXX !!! ERROR = BASE64 [CODEFORMAT IS INVALID] = ERROR !!! XXXXX")
					dialog.ok(addon_id, translation(30506))
					self.clear_credentials(forceRefresh=True)
		elif its_base64 and force_encrypt is False:
			debug_MS(f"(references.specs_decrypt[3]) XXX FORCE_ENCRYPT : {str(force_encrypt)} || !!! ATTENTION = YOUR CREDENTIAL '{course}' IS IN BASE64-FORMAT = ATTENTION !!! XXX")
			return data
		elif not its_base64 and force_encrypt is False:
			debug_MS(f"(references.specs_decrypt[4]) XXX FORCE_ENCRYPT : {str(force_encrypt)} || '{course}' IS NORMAL - NOT BASE64-ENCODED XXX")
			return data
		else:
			if course == 'PASSWORD':
				failing("(references.specs_decrypt[5]) XXXXX !!! ERROR = BASE64 [CODEFORMAT IS INVALID] = ERROR !!! XXXXX")
				dialog.ok(addon_id, translation(30506))
				self.clear_credentials(forceRefresh=True)
		return ""

	def has_credentials(self, forceDebug=True):
		if forceDebug is True:
			debug_MS("(references.has_credentials) ### START has_credentials ###")
		if self.username is not None and self.password is not None:
			if len(self.username) > 0 and len(self.password) >= 6:
				return True
		else:
			xbmc.sleep(3000)
			if self.username is not None and self.password is not None:
				if len(self.username) > 0 and len(self.password) >= 6:
					return True
		return False

	def get_credentials(self):
		debug_MS("(references.get_credentials) ### START get_credentials ###")
		return (self.specs_decrypt(self.username, 'USERNAME'), self.specs_decrypt(self.password, 'PASSWORD'))

	def save_credentials(self):
		debug_MS("(references.save_credentials) ### START save_credentials ###")
		USER = dialog.input(translation(30671), type=xbmcgui.INPUT_ALPHANUM)
		PASSWORD = dialog.input(translation(30672), type=xbmcgui.INPUT_ALPHANUM)
		ENCRYPTION = dialog.yesno(addon_id, translation(30507).format(addon_name))
		if ENCRYPTION:
			_user = self.specs_encrypt(USER) if USER != '' else USER
			_code = self.specs_encrypt(PASSWORD) if PASSWORD != '' else PASSWORD
			_cipher = 'JA - ENCRYPTED'
			debug_MS(f"(references.save_credentials[1]) XXX encrypted-USER : {_user} || encrypted-PASSWORD : {_code} || ENCRYPTION : {_cipher} XXX")
		else:
			_user = USER
			_code = PASSWORD
			_cipher = 'NEIN - NICHT ENCRYPTED'
			debug_MS(f"(references.save_credentials[2]) XXX standard-USER : {_user} || standard-PASSWORD : {_code} || ENCRYPTION : {_cipher} XXX")
		NAME = USER
		addon.setSetting('username', _user)
		addon.setSetting('password', _code)
		addon.setSetting('encrypted', _cipher)
		return (NAME, USER, PASSWORD)

	def clear_credentials(self, clearTries=False, forceRefresh=False):
		debug_MS("(references.clear_credentials) ### START clear_credentials ###")
		addon.setSetting('username', '')
		addon.setSetting('password', '')
		addon.setSetting('verified_account', 'false')
		addon.setSetting('license_ending', '')
		addon.setSetting('encrypted', '')
		addon.setSetting('authtoken', '0')
		addon.setSetting('login_status', '0')
		addon.setSetting('liveFree', 'false')
		addon.setSetting('livePay', 'false')
		addon.setSetting('vodFree', 'false')
		addon.setSetting('vodPay', 'false')
		addon.setSetting('high_definition', 'false')
		if xbmcvfs.exists(self.signed_file) and os.path.exists(self.signed_file):
			shutil.rmtree(self.tempSIGNED_folder, ignore_errors=True)
		if xbmcvfs.exists(self.free_file) and os.path.exists(self.free_file):
			shutil.rmtree(self.tempFREE_folder, ignore_errors=True)
		if addon.getSetting('login_status') == '0' and addon.getSetting('verified_account') == 'false':
			if clearTries is True:
				addon.setSetting('maximum_tries', '1')
			if forceRefresh is True:
				xbmc.sleep(3000)
				xbmc.executebuiltin('Container.Refresh')
			return True
		return False
