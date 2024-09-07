# -*- coding: utf-8 -*-

from .common import *
from .references import Registration


def _header(SENDTOKEN=False, REFERRER=None, USERTOKEN=None):
	header = {}
	header['Pragma'] = 'no-cache'
	header['Accept'] = 'application/json, application/x-www-form-urlencoded, text/plain, */*'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.8,en;q=0.7'
	header['Origin'] = 'https://plus.rtl.de'
	if REFERRER:
		header['Referer'] = REFERRER
	if SENDTOKEN and USERTOKEN:
		if USERTOKEN.startswith('Bearer'):
			header['Authorization'] = USERTOKEN
		else:
			header['x-auth-token'] = USERTOKEN
	return header

class Transmission(object):

	def __init__(self):
		self.references = Registration
		self.maxTokenTime = 24*60*60 # max. Token-Time (Seconds) before clear the Token and delete Token-File [6*60*60 = 6 hours | 12*60*60 = 12 hours | 24*60*60 = 24 hours]
		self.tempSIGNED_folder = tempSIGNED
		self.signed_file = signedFile
		self.tempFREE_folder = tempFREE
		self.free_file = freeFile
		self.LOCAL_CLEAR = datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
		self.LOCAL_TIME = int(round(datetime.now().timestamp()))
		self.verify_connection = (True if addon.getSetting('verify_ssl') == 'true' else False)
		self.AUTH_CODE = addon.getSetting('authtoken')
		self.max_tries = (int(addon.getSetting('maximum_tries')) if addon.getSetting('maximum_tries') != "" else 1)
		self.store = cache
		self.session = requests.Session()
		if params.get('mode') !='create_account':
			self.load_session()

	def save_content(self, title, filename=None, foldername=None, text=""):
		debug_MS(f"(utilities.save_content) ### SAVE NEW-FILE : * {title} * ###")
		if foldername is not None and not xbmcvfs.exists(foldername) and not os.path.exists(foldername):
			xbmcvfs.mkdirs(foldername)
		if filename is not None and text != "":
			with open(filename, 'w') as save:
				json.dump(text, save, indent=4, sort_keys=True)

	def clear_content(self, title, filename=None, foldername=None):
		debug_MS(f"(utilities.clear_content) ### DELETE OLD-FILE : * {title} * ###")
		if filename is not None and xbmcvfs.exists(filename):
			if foldername is not None and xbmcvfs.exists(foldername) and os.path.exists(foldername):
				shutil.rmtree(foldername, ignore_errors=True)

	def record_specs(self, DETAILS, ACCOUNT=False):
		debug_MS(f"(utilities.record_specs) ### START ...record_specs - isAccount = {str(ACCOUNT)} ###")
		b64_string = DETAILS.split('.')[1]
		b64_string += "=" * ((4 - len(b64_string) % 4) % 4)
		RESULTS = json.loads(base64.b64decode(b64_string))
		debug_MS(f"(utilities.record_specs[1]) ##### jsonDATA-Token base64-decoded : {RESULTS} #####")
		CLIENT_ID, (MAC_CLEAR, MAC_CODE) = RESULTS.get('clientId'), Registration().get_mac_key()
		NOW_CLEAR, NOW_TIME = self.LOCAL_CLEAR, self.LOCAL_TIME
		if RESULTS.get('iat', '') and RESULTS.get('exp', '') and RESULTS.get('licenceEndDate', ''):
			ONE_CLEAR, ONE_TIME = self.convert_times(RESULTS['iat'], RESULTS['licenceEndDate'][:19], 'CET_BASE'), self.convert_times(RESULTS['iat'], RESULTS['licenceEndDate'][:19], 'CET_INT')
			TWO_CLEAR, TWO_TIME = self.convert_times(RESULTS['iat'], RESULTS['exp'], 'CET_BASE'), self.convert_times(RESULTS['iat'], RESULTS['exp'], 'CET_INT')
			if TWO_TIME < ONE_TIME:
				EXP_CLEAR, EXP_TIME = TWO_CLEAR, TWO_TIME
			else:
				EXP_CLEAR, EXP_TIME = ONE_CLEAR, ONE_TIME
		elif RESULTS.get('iat', '') and RESULTS.get('exp', '') and not RESULTS.get('licenceEndDate'):
			EXP_CLEAR, EXP_TIME = self.convert_times(RESULTS['iat'], RESULTS['exp'], 'CET_BASE'), self.convert_times(RESULTS['iat'], RESULTS['exp'], 'CET_INT')
		HAS_PACK, MAX_STREAMS = RESULTS.get('hasAcquiredPackages', False), RESULTS.get('maxParallelStreams', 1)
		CODING = {'clientId': CLIENT_ID,
							'macAdress': MAC_CLEAR,
							'accessToken': DETAILS,
							'startingClear': NOW_CLEAR,
							'startingTime': NOW_TIME,
							'expiringClear': EXP_CLEAR,
							'expiringTime': EXP_TIME,
							'hasPackages': HAS_PACK,
							'maxStreams': MAX_STREAMS}
		debug_MS(f"(utilities.record_specs[2]) ### NEW TOKENFILE CREATED : {str(CODING)} ###")
		if ACCOUNT is True:
			self.clear_content('SIGNED_TOKEN', self.signed_file, self.tempSIGNED_folder)
			self.save_content('SIGNED_TOKEN', self.signed_file, self.tempSIGNED_folder, CODING)
		else:
			self.clear_content('FREE_TOKEN', self.free_file, self.tempFREE_folder)
			self.save_content('FREE_TOKEN', self.free_file, self.tempFREE_folder, CODING)

	def load_session(self):
		debug_MS("(utilities.load_session) ### START load_session ###")
		forceRenew, CONTENT, SIGNED, FAILS = (False for _ in range(4))
		NEWSTATE = (True if addon.getSetting('login_status') in ['2', '3'] else False)
		NEWAUDIT = (True if addon.getSetting('verified_account') == 'true' else False)
		if self.AUTH_CODE != '0' and self.references().has_credentials(forceDebug=False) is True:
			if ((not xbmcvfs.exists(self.signed_file) and not os.path.exists(self.signed_file)) or \
				(xbmcvfs.exists(self.signed_file) and os.path.exists(self.signed_file) and NEWSTATE is False and NEWAUDIT is False)):
				SIGNED, FAILS, forceRenew = (True for _ in range(3))
		if FAILS is False and xbmcvfs.exists(self.signed_file) and os.path.exists(self.signed_file):
			CONTENT, SIGNED = self.signed_file, True
		if FAILS is False and CONTENT is False and xbmcvfs.exists(self.free_file) and os.path.exists(self.free_file):
			CONTENT, SIGNED = self.free_file, False
		if CONTENT:
			try:
				with open(CONTENT, 'r') as publish:
					ACC_DATA = json.load(publish)
					USER_TOKEN, EXP_CLEAR, EXP_TIME, TOKEN_MAX = ACC_DATA['accessToken'], ACC_DATA['expiringClear'], ACC_DATA['expiringTime'], ACC_DATA['startingTime'] + self.maxTokenTime
				debug_MS(f"(utilities.load_session[1]) ##### SESSION-Time (local NOW) = {str(self.LOCAL_CLEAR)} || VALID until (local EXP) = {str(EXP_CLEAR)} #####")
				if (self.LOCAL_TIME + 60) < EXP_TIME and self.LOCAL_TIME < TOKEN_MAX: # LOCAL Datetime now - 1 minute for Safety
					debug_MS("(utilities.load_session[2]) ##### NOTHING CHANGED - TOKENFILE OKAY #####")
					self.AUTH_CODE = USER_TOKEN
					return True
				else:
					debug_MS("(utilities.load_session[3]) ##### !!! EXPIRED = TOKENFILE [MAX. LIFETIME OF TOKEN IS REACHED] = EXPIRED !!! #####")
					forceRenew = True
			except:
				failing("(utilities.load_session[4]) XXXXX !!! ERROR = TOKENFILE [TOKENFORMAT IS INVALID] = ERROR !!! XXXXX")
				forceRenew = True
		else:
			debug_MS("(utilities.load_session[5]) ##### NOTHING FOUND - CREATE TOKENFILE #####")
			forceRenew = True
		if forceRenew:
			if xbmcvfs.exists(self.signed_file) and os.path.exists(self.signed_file):
				self.clear_content('SIGNED_TOKEN', self.signed_file, self.tempSIGNED_folder)
			if xbmcvfs.exists(self.free_file) and os.path.exists(self.free_file):
				self.clear_content('FREE_TOKEN', self.free_file, self.tempFREE_folder)
			if SIGNED:
				self.renewal_login()
			else:
				self.anonymous_token()

	def renewal_login(self):
		if self.references().has_credentials() is True:
			USER, PWD = self.references().get_credentials()
		else:
			NAME, USER, PWD = self.references().save_credentials()
		return self.register_account(USER, PWD, forceLogin=True)

	def check_utc(self, value):
		START = self.LOCAL_TIME - (10*60) # Local-Time minus 10 minutes
		STOPP = self.LOCAL_TIME + (10*60) # Local-Time plus 10 minutes
		if START <= int(value) <= STOPP:
			return False # TIME IS LOCAL-TIME
		return True # TIME IS UTC-TIME

	def convert_times(self, actual, expire, FORM=""):
		STARTING, ENDING = (False for _ in range(2))
		if isinstance(actual, (int, float)) and isinstance(expire, (int, float)):
			STARTING, ENDING = actual, expire
		elif isinstance(actual, (int, float)) and isinstance(expire, str):
			CIPHER = datetime(*(time.strptime(expire, '%Y-%m-%dT%H:%M:%S')[0:6]))# 2023-11-05T22:03:43+00:00
			STARTING, ENDING = actual, int(round(CIPHER.timestamp()))
		if STARTING and ENDING:
			if self.check_utc(STARTING) is True:
				CLOCK = TGM(time.localtime(ENDING))
				debug_MS(f"(utilities.convert_times[1]) IT IS UTC-TIME ##### Actual-Time (local NOW) = {str(self.LOCAL_TIME)} || Actual-Time (input IAT) = {str(STARTING)} #####")
				debug_MS(f"(utilities.convert_times[1]) IT IS UTC-TIME ##### Expire-Time (input) = {str(expire)} || Expire-Time (output) = {str(CLOCK)} #####")
				if FORM == 'CET_BASE':
					CIPHER = datetime(1970,1,1) + timedelta(seconds=int(CLOCK))
					return CIPHER.strftime('%d.%m.%Y - %H:%M:%S')
				return CLOCK
			elif self.check_utc(STARTING) is False and FORM == 'CET_INT':
				debug_MS(f"(utilities.convert_times[2]) CET-TIME ##### Actual-Time (local NOW) = {str(self.LOCAL_TIME)} || Actual-Time (input IAT) = {str(STARTING)} #####")
				debug_MS(f"(utilities.convert_times[2]) CET-TIME ##### Expire-Time (input) = {str(expire)} || Expire-Time (output) = {str(ENDING)} #####")
				return ENDING
			elif self.check_utc(STARTING) is False and FORM == 'CET_BASE':
				if isinstance(expire, (int, float)):
					debug_MS(f"(utilities.convert_times[3]) CET-TIME ##### Actual-Time (local NOW) = {str(self.LOCAL_TIME)} || Actual-Time (input IAT) = {str(STARTING)} #####")
					debug_MS(f"(utilities.convert_times[3]) CET-TIME ##### Expire-Time (input) = {str(expire)} || Expire-Time (output) = {str(ENDING)} #####")
					return time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime(ENDING))
				debug_MS(f"(utilities.convert_times[4]) CET-TIME ##### Actual-Time (local NOW) = {str(self.LOCAL_TIME)} || Actual-Time (input IAT) = {str(STARTING)} #####")
				debug_MS(f"(utilities.convert_times[4]) CET-TIME ##### Expire-Time (input) = {str(expire)} || Expire-Time (output) = {str(ENDING)} #####")
				return CIPHER.strftime('%d.%m.%Y - %H:%M:%S')
		else:
			failing(f"(utilities.convert_times) XXXXX !!! ERROR =  KANN KEIN ZEITSEGMENT ERSTELLEN FÜR XXXXX Actual-Time : {str(actual)} === Expire-Time : {str(expire)} = ERROR !!! XXXXX")

	def register_account(self, username, password, forceLogin=False):
		debug_MS(f"(utilities.register_account) >>>>> START OF LOGIN-PROCESS : forceLogin = {str(forceLogin)} || maxTRIES = {str(self.max_tries)}/3 >>>>>")
		USER_TOKEN = '0'
		if forceLogin is False and xbmcvfs.exists(self.signed_file) and os.path.exists(self.signed_file):
			with open(self.signed_file, 'r') as account:
				ACC_DATA = json.load(account)
				USER_TOKEN, EXP_CLEAR, EXP_TIME, TOKEN_MAX = ACC_DATA['accessToken'], ACC_DATA['expiringClear'], ACC_DATA['expiringTime'], ACC_DATA['startingTime'] + self.maxTokenTime
			debug_MS(f"(utilities.register_account) ##### SESSION-Time (local NOW) = {str(self.LOCAL_CLEAR)} || VALID until (local EXP) = {str(EXP_CLEAR)} #####")
			if (self.LOCAL_TIME + 60) < EXP_TIME and self.LOCAL_TIME < TOKEN_MAX: # LOCAL-TIME now plus 1 minute for Safety
				self.AUTH_CODE = USER_TOKEN
				return True
		addon.setSetting('last_registstration', self.LOCAL_CLEAR)
		payload = {'email': username, 'password': password}
		ACCOUNT_LOGIN = self.retrieveCONTENT(LOGIN_LINK, 'PUSH', 'https://plus.rtl.de/', json=payload)
		if self.max_tries > 3:
			addon.setSetting('username', '')
			addon.setSetting('password', '')
			addon.setSetting('license_ending', '[B]!!! ERROR - ERROR !!![/B]')
			addon.setSetting('verified_account', 'false')
			dialog.ok(addon_id, translation(30508))
			self.clear_content('SIGNED_TOKEN', self.signed_file, self.tempSIGNED_folder)
			return False
		elif ACCOUNT_LOGIN.status_code == 200:
			log("(utilities.register_account) ++++++++++++++++++++++++++++++++++++++++++++++++++++")
			log("(utilities.register_account) ++++++ !!! DU BIST ERFOLGREICH EINGELOGGT !!! ++++++")
			log("(utilities.register_account) ++++++++++++++++++++++++++++++++++++++++++++++++++++")
			USER_TOKEN = (ACCOUNT_LOGIN.json().get('access_token') or ACCOUNT_LOGIN.json().get('token'))
			debug_MS(f"(utilities.register_account) ##### SIGNED-TOKEN : {str(USER_TOKEN)} #####")
			addon.setSetting('authtoken', USER_TOKEN)
			self.AUTH_CODE = USER_TOKEN
			self.record_specs(USER_TOKEN, ACCOUNT=True)
			self.verify_premium(USER_TOKEN)
			return True
		else:
			failing("(utilities.register_account) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
			failing("(utilities.register_account) XXXXX !!! ERROR = DU BIST NICHT EINGELOGGT = ERROR !!! XXXXX")
			failing(f"(utilities.register_account) XXXXX SERVER-ANTWORT = {str(ACCOUNT_LOGIN.text)} XXXXX")
			failing("(utilities.register_account) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
			addon.setSetting('license_ending', '[B]!!! ERROR - ERROR !!![/B]')
			addon.setSetting('verified_account', 'false')
			addon.setSetting('encrypted', '')
			addon.setSetting('authtoken', '0')
			addon.setSetting('login_status', '0')
			addon.setSetting('liveFree', 'false')
			addon.setSetting('livePay', 'false')
			addon.setSetting('vodFree', 'false')
			addon.setSetting('vodPay', 'false')
			addon.setSetting('high_definition', 'false')
			if addon.getSetting('maximum_tries') != "":
				next_test = str(int(addon.getSetting('maximum_tries'))+1)
				addon.setSetting('maximum_tries', next_test)
			self.clear_content('SIGNED_TOKEN', self.signed_file, self.tempSIGNED_folder)
		return False

	def verify_premium(self, FACTS):
		addon.setSetting('license_ending', '')
		addon.setSetting('verified_account', 'false')
		addon.setSetting('login_status', '0')
		addon.setSetting('liveFree', 'false')
		addon.setSetting('livePay', 'false')
		addon.setSetting('vodFree', 'false')
		addon.setSetting('vodPay', 'false')
		b64_parts = FACTS.split('.')[1]
		b64_parts += "=" * ((4 - len(b64_parts) % 4) % 4)
		RECEIVED = json.loads(base64.b64decode(b64_parts))
		if RECEIVED.get('iat', '') and RECEIVED.get('licenceEndDate', ''):
			UNO_CLEAR = self.convert_times(RECEIVED['iat'], RECEIVED['licenceEndDate'][:19], 'CET_BASE')
			LIC_ENDING = UNO_CLEAR[:-3].replace(' - ', ' • ')
		elif RECEIVED.get('iat', '') and RECEIVED.get('exp', ''):
			DUE_CLEAR = self.convert_times(RECEIVED['iat'], RECEIVED['exp'], 'CET_BASE')
			LIC_ENDING = DUE_CLEAR[:-3].replace(' - ', ' • ')
		else: LIC_ENDING = 'DATE NOT FOUND'
		CHECK = RECEIVED['permissionsV2'] if RECEIVED.get('permissionsV2', '') else RECEIVED['permissions'] if RECEIVED.get('permissions', '') else None
		PRIVILEGE = CHECK['streaming'] if CHECK and CHECK.get('streaming', '') else None
		if PRIVILEGE and PRIVILEGE.get('livestreamAccessToFreeTv', '') is True:
			addon.setSetting('liveFree', 'true')
		if PRIVILEGE and PRIVILEGE.get('livestreamAccessToPayTv', '') is True:
			addon.setSetting('livePay', 'true')
			addon.setSetting('verified_account', 'true')
			addon.setSetting('login_status', '3')
		if PRIVILEGE and PRIVILEGE.get('vodAccessToFreeContent', '') is True:
			addon.setSetting('vodFree', 'true')
		if PRIVILEGE and PRIVILEGE.get('vodAccessToPayContent', '') is True:
			addon.setSetting('vodPay', 'true')
			addon.setSetting('verified_account', 'true')
			addon.setSetting('login_status', '3')
		debug_MS(f"(utilities.verify_premium[1]) ##### END-CHECK = Setting(liveGratis)  : {str(addon.getSetting('liveFree'))} #####")
		debug_MS(f"(utilities.verify_premium[1]) ##### END-CHECK = Setting(livePremium) : {str(addon.getSetting('livePay'))} #####")
		debug_MS(f"(utilities.verify_premium[1]) ##### END-CHECK = Setting(vodGratis)   : {str(addon.getSetting('vodFree'))} #####")
		debug_MS(f"(utilities.verify_premium[1]) ##### END-CHECK = Setting(vodPremium)  : {str(addon.getSetting('vodPay'))} #####")
		if RECEIVED.get('subscriptionState', '') in [4, 5]:
			log(f"(utilities.verify_premium[2]) ##### Paying-Member : SubscriptionState Number * {str(RECEIVED['subscriptionState'])} * = (Account is OK) #####")
			addon.setSetting('verified_account', 'true')
			addon.setSetting('login_status', '3')
			addon.setSetting('license_ending', f"[B]PREM[/B]  -  {str(LIC_ENDING)}")
		if addon.getSetting('login_status') != '3':
			GUEST = (RECEIVED.get('guest', '') is True or RECEIVED.get('isGuest', '') is True)
			if GUEST is True:
				addon.setSetting('login_status', '1')
				log("(utilities.verify_premium[2]) ##### Free-Anonymous = (Your Guest-Account is OK) #####")
			else:
				addon.setSetting('verified_account', 'true')
				addon.setSetting('login_status', '2')
				addon.setSetting('license_ending', f"[B]FREE[/B]  -  {str(LIC_ENDING)}")
				log("(utilities.verify_premium[2]) ##### Free-Member = (Your Free-Account is OK) #####")
			addon.setSetting('high_definition', 'false')
		debug_MS("(utilities.verify_premium) <<<<< END OF LOGIN-PROCESS OR FETCHING ANONYMOUS-TOKEN <<<<<")

	def anonymous_token(self):
		debug_MS(f"(utilities.anonymous_token) >>>>> START OF FETCHING ANONYMOUS-TOKEN >>>>>")
		USER_TOKEN, COVERT = '0', False
		addon.setSetting('last_registstration', self.LOCAL_CLEAR)
		try:
			STARTING = self.retrieveCONTENT('https://plus.rtl.de', 'LOAD', 'https://plus.rtl.de/')
			SCRIPT = re.compile(r'<script src="(main[A-z0-9\-\.]+\.js)"', re.S).findall(STARTING)[-1]
			LOADING = self.retrieveCONTENT(f"https://plus.rtl.de/{SCRIPT}", 'LOAD', 'https://plus.rtl.de/')
			COVERT = re.compile(r'anonymousCredentials:{([^}]+)}', re.S).findall(LOADING)[0]
		except:
			failing("(utilities.anonymous_token) ERROR - TOKEN - ERROR XXXXX !!! FREE-TOKEN : ANONYME ZUGANGSDATEN NICHT GEFUNDEN !!! XXXXX")
			dialog.notification(translation(30521).format('*ANONYME ZUGANGSDATEN* NICHT GEFUNDEN', ''), translation(30581), icon, 12000)
		if COVERT:
			CLEAR_DATA = re.sub(r'([a-zA-Z0-9_-]+)', r'"\1"', COVERT.replace('"', ''))
			SECRETS = json.loads(f"{{{CLEAR_DATA}}}")
			debug_MS(f"(utilities.anonymous_token) ### SECRETS FOR TOKEN-REQUEST : {str(SECRETS)} ### ")
			AUTH_URL = base64.b64decode(b'aHR0cHM6Ly9hdXRoLnJ0bC5kZS9hdXRoL3JlYWxtcy9ydGxwbHVzL3Byb3RvY29sL29wZW5pZC1jb25uZWN0L3Rva2Vu').decode()
			TOKEN_QUEST = self.retrieveCONTENT(AUTH_URL, 'PUSH', 'https://plus.rtl.de/', data=SECRETS)
			if TOKEN_QUEST.status_code == 200:
				log("(utilities.anonymous_token) ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
				log("(utilities.anonymous_token) ++++++ !!! DER ANONYME-TOKEN WURDE ERFOLGREICH ÜBERTRAGEN !!! ++++++")
				log("(utilities.anonymous_token) ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
				USER_TOKEN = (TOKEN_QUEST.json().get('access_token') or TOKEN_QUEST.json().get('token'))
				debug_MS(f"(utilities.anonymous_token) ### FREE-TOKEN : {str(USER_TOKEN)} ###")
				addon.setSetting('authtoken', USER_TOKEN)
				self.AUTH_CODE = USER_TOKEN
				self.record_specs(USER_TOKEN)
				self.verify_premium(USER_TOKEN)
				return True
			else:
				failing(f"(utilities.anonymous_token) ERROR - TOKEN - ERROR XXXXX !!! SERVER-ANTWORT AUF ABFRAGE DER ANONYMEN ZUGANGSDATEN : {TOKEN_REQUEST.text} !!! XXXXX ")
		return False

	def verify_token(self):
		return (True if addon.getSetting('verified_account') == 'true' else False)

	def makeREQUEST(self, url, method='GET', REF=None):
		content = self.store.cacheFunction(self.retrieveCONTENT, url, method, REF)
		return content

	def retrieveCONTENT(self, url, method='GET', REF=None, headers=None, cookies=None, allow_redirects=True, stream=None, data=None, json=None):
		SENDTOKEN = True if method in ['GET', 'TRACK'] and self.verify_token() is True and self.AUTH_CODE != '0' else False
		REALCODE = f"Bearer {self.AUTH_CODE}" if addon.getSetting('login_status') == '1' else self.AUTH_CODE
		ANSWER = None
		try:
			if method in ['GET', 'LOAD', 'TRACK']:
				result = self.session.get(url, headers=_header(SENDTOKEN, REF, REALCODE), allow_redirects=allow_redirects, verify=self.verify_connection, stream=stream, timeout=30)
			elif method in ['POST', 'PUSH']:
				result = self.session.post(url, headers=_header(SENDTOKEN, REF, REALCODE), allow_redirects=allow_redirects, verify=self.verify_connection, data=data, json=json, timeout=30)
			ANSWER = result.json() if method in ['GET', 'POST'] else result.text if method == 'LOAD' else result
			debug_MS(f"(utilities.retrieveCONTENT) === CALLBACK === STATUS : {str(result.status_code)} || URL : {result.url} || HEADER : {_header(SENDTOKEN, REF, REALCODE)} ===")
		except requests.exceptions.RequestException as e:
			failing(f"(utilities.retrieveCONTENT) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {str(e)} #####")
			dialog.notification(translation(30521).format('URL', ''), translation(30523).format(str(e)), icon, 12000)
			return sys.exit(0)
		return ANSWER
