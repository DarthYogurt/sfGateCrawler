import urllib2
import time

from bs4 import BeautifulSoup



def crawlSFGate(url):
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page)

	#targetUrls = soup.findAll('a', attrs = {'class':'serp_click_2 event_detail_link'})
	targetUrls = soup.findAll('td', attrs = {'class':'title_content'})
	test = []

	#for targetUrl in targetUrls:
	#	time.sleep(1)
	for i in range(1): 
		targetUrl = targetUrls[0]
		AObject = targetUrl.next_element.next_element.attrs	# gets the <a class: ..... element
		
		sfGateEventID 	= AObject['data-z-event-id']
		sfGateEventRank = AObject['data-z-rank']
		sfGateEventSponsored 	= AObject['data-z-sponsored']
		try:	sfGateEventCanceled  	= AObject['data-z-event-canceled']  #eventCancelled not set all the time
		except: sfGateEventCanceled 	= 0
		try:	eventURL 		= AObject['href']
		except:	eventURL = ""
		
		#Actual Event Page,  Soup initialize for deeper webpage
		bSoup = BeautifulSoup(urllib2.urlopen(eventURL))
		
		#Event Name  
		eventTitle 		= bSoup.find('span', attrs = {'class':'summary'}).contents[0]
		
		#Parsing Time
		try:	startTime = str(bSoup.find('abbr', attrs = {'class':'dtstart'}).attrs['title'])
		except:	startTime=""
		eventStartDate	= startTime[:startTime.find("T")]
		eventStartTime	= startTime[startTime.find("T")+1:startTime.find("Z")]
		
		try:	eventText       = bSoup.find('abbr', attrs = {'class':'dtstart'}).contents[0]
		except:	eventText=""
		sfGateBreadcrumb= bSoup.find('span', attrs = {'itemprop':'breadcrumb'}).findAll('a')[-1]  #Gets a list of all the Breadcrumbs <a href> and takes last one [-1]
		
		#Venue
		venue 			= bSoup.find('div', attrs = {'class':'venue'}).next_element.next_element
		venueID			= venue.attrs['data-z-destination-venue-id']
		venueURL		= venue.attrs['href']
		venueName		= venue.contents[0]

		#Venue Description
		try:
			excerptLess		= bSoup.find('span', attrs = {'class':'excerpt'}).contents
			excerptMore		= bSoup.find('span', attrs = {'class':'excerpted hidden'}).contents
			excerpt = ""
			for i in range(len(excerptLess)):	
				try:	excerpt = excerpt + excerptLess[i].string
				except:	True
			for i in range(len(excerptMore)):	
				try:	excerpt = excerpt + excerptMore[i].string
				except:	True
			venueDescription = excerpt
		except:	venueDescription = ""
		
		try:	eventWebsite	= str(bSoup.find('div', attrs = {'class' : 'detail'}).next_element.next_element.attrs['href'])
		except:	eventWebsite = ""
		try:	eventPhone	= bSoup.find_all('span', attrs = {'class':'title'},text="Phone")[0].next_sibling.string
		except:	eventPhone = ""
		try:	eventPrice		= bSoup.find_all('span', attrs = {'class':'title'},text="Price")[0].next_sibling.string
		except: eventPrice = ""
		try:	ageSuitability 	= bSoup.find_all('span', attrs = {'class':'title'},text="Age Suitability")[0].next_sibling.string
		except:	ageSuitability = ""
		
		#SFGATE Categories
		try:
			categoriesRaw = bSoup.find_all('span', attrs = {'class':'title'},text="Categories")[0].parent.findAll('a')
			categories = ""
			for cat in categoriesRaw:
				if categories == "":	categories = str(cat.text)
				else:	categories = categories + "," + str(cat.text)
			sfGateCategory = categories
		except: sfGateCategory = ""
		
		#SFGateTags
		sfGateTags = ""
		tagsRaw = bSoup.find_all('span', attrs = {'id':'taglist'})[0].findAll('a')
		for tag in tagsRaw:
			if sfGateTags == "":	sfGateTags = str(tag.text)
			else:	sfGateTags = sfGateTags + "," + str(tag.text)
		
		#Adress
		try:	addressStreet 		= bSoup.find('span', attrs = {'class':'street-address'}).contents[0]
		except:	addressStreet = ""
		try:	addressLocality		= bSoup.find('span', attrs = {'class':'locality'}).contents[0]
		except:	addressLocality = ""
		try:	addressRegion		= bSoup.find('span', attrs = {'class':'region'}).contents[0]
		except:	addressRegion=""
		try:	addressPostalCode= bSoup.find('span', attrs = {'class':'postal-code'}).contents[0]
		except:	addressPostalCode=""
		try:	sfGateImageURL 	= bSoup.find('div' , attrs = {'class':'main_image'}).next_element.next_element.attrs['src']
		except:	sfGateImageURL=""
		try:	sfGateCreator   		= bSoup.find('strong',text="Creator:").parent.find('a').text
		except:	sfGateCreator=""
		
	# PIckup Next Page
	try:	nextPage = "http://events.sfgate.com"+str(soup.find('div',attrs={"class":"pager"}).find('a').attrs['href'])
	except:	nextPage = 0
	#print 		"RETURNING ",nextPage
	#print type(str(nextPage))
	return nextPage

url = "http://events.sfgate.com/search?srad=85.0&swhat=&swhen=Next+30+Days&swhere=San+Francisco%2C+CA&st=event&new=n&srss=50"

while url !=0:
	print url
	url = crawlSFGate(url)




