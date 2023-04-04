from datetime import datetime
from typing import List
import urllib.request, json

header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
			'AppleWebKit/537.11 (KHTML, like Gecko) '
			'Chrome/23.0.1271.64 Safari/537.11',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			'Accept-Encoding': 'none',
			'Accept-Language': 'en-US,en;q=0.8',
			'Connection': 'keep-alive'}
url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
request = urllib.request.Request(url, None, header)

#YGOPRODECK API keys
DATA = 'data'
BANLIST_INFO = 'banlist_info'
BAN_TCG = 'ban_tcg'
CARD_IMAGES = 'card_images'
CARD_TYPE = 'type'
BANLIST_INFO = 'banlist_info'
BAN_TCG = 'ban_tcg'
NAME = 'name'
CARD_ID = 'id'

#Token stuff
TOKEN = 'Token'
SKILL = 'Skill Card'

#Banlist stuff

BANNED = 'Banned'
LIMITED = 'Limited'
SEMILIMITED = 'Semi-Limited'
UNLIMITED = 'Unlimited'

banlistPath = 'banlist/gods.lflist.conf'
jsonBanlist = 'json/gods_banlist.json'

cards = {}

additionalForbidden = []
additionalLimited = []
additionalSemiLimited = []
additionalUnlimited = []

class Card:

	def __init__(self, cardName:str, cardId: int, status:int):
		self.cardName = cardName
		self.cardId = cardId
		self.status = status


with open(jsonBanlist) as banlistFile:
	banlist = json.load(banlistFile)
	additionalForbidden = banlist.get(BANNED)
	additionalLimited = banlist.get(LIMITED)
	additionalSemiLimited = banlist.get(SEMILIMITED)
	additionalUnlimited = banlist.get(UNLIMITED)

with urllib.request.urlopen(request) as url:
	cards = json.loads(url.read().decode()).get(DATA)

banlist: List[Card] = []

for card in cards:
	cardType = card.get(CARD_TYPE)
	if (cardType != TOKEN and cardType != SKILL):
		banInfo = card.get(BANLIST_INFO)
		if (banInfo == None):
			status = 3	
		if (banInfo != None):
			banlistStatus = banInfo.get(BAN_TCG)
			if (banlistStatus == None):
				status = 3
			if (banlistStatus == BANNED):
				status = 0
			if (banlistStatus == LIMITED):
				status = 1
			if (banlistStatus == SEMILIMITED):
				status = 2
			if (banlistStatus == UNLIMITED):
				status = 3

		cardName = card.get(NAME)

		if cardName in additionalForbidden:
			additionalForbidden.remove(cardName)
			status = 0
		if cardName in additionalLimited:
			additionalLimited.remove(cardName)
			status = 1
		if cardName in additionalSemiLimited:
			additionalSemiLimited.remove(cardName)
			status = 2
		if cardName in additionalUnlimited:
			additionalUnlimited.remove(cardName)
			status = 3

		
		for image in card.get(CARD_IMAGES):
			cardId = image.get(CARD_ID)
			banlist.append(Card(cardName, cardId, status))

with open(banlistPath, 'w', encoding="utf-8") as lflist:

	print(additionalForbidden)
	print(additionalLimited)
	print(additionalSemiLimited)
	print(additionalUnlimited)

	today = datetime.now()
	lflist.write("#[GODS Format]\n")
	lflist.write("!GODS Format %s\n"% today.strftime("%m.%Y"))
	lflist.write("$whitelist\n")
	for card in banlist:
		lflist.write("%d %d -- %s\n" % (card.cardId, card.status, card.cardName))
	
