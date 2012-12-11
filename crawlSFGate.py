#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import time, sys, uuid, json, codecs, getopt, datetime
from couchbase import Couchbase
import hashlib

from connector import connector
SERVER_NAME = connector.SERVER_NAME
SERVER_PORT = connector.SERVER_PORT
USERNAME 	= connector.USERNAME
PASSWORD 	= connector.PASSWORD
CB_BUCKET_NAME = connector.CB_BUCKET_NAME

couchbase = Couchbase("%s:%s" % (SERVER_NAME, SERVER_PORT), username=USERNAME, password=PASSWORD)
bucket = couchbase[CB_BUCKET_NAME]

# Creates a "Hex Key" to make a UUID for each object in Bucket
def getKey(key):	return hashlib.sha1(key).hexdigest()[0:10]


def crawlSFGate(url):
	try:	page = urllib2.urlopen(url)
	except:	page = ""
	soup = BeautifulSoup(page)

	#targetUrls = soup.findAll('a', attrs = {'class':'serp_click_2 event_detail_link'})
	targetUrls = soup.findAll('td', attrs = {'class':'title_content'})
	test = []

	#for targetUrl in targetUrls:
	#	time.sleep(10)
	for i in range(1): 
		targetUrl = targetUrls[0]
		AObject = targetUrl.next_element.next_element.attrs	# gets the <a class: ..... element
		
		#SFGATE Specific HTML Data
		sfGateEventID 	 = AObject['data-z-event-id']
		sfGateEventRank = AObject['data-z-rank']
		sfGateEventSponsored 	= AObject['data-z-sponsored']
		try:	sfGateEventCanceled  	= AObject['data-z-event-canceled']  #eventCancelled not set all the time
		except: sfGateEventCanceled 	= 0
		try:	eventURL 		= AObject['href']		#Used to get webpage of event so that can crawl deeper
		except:	eventURL = ""
		
		#Actual Event Page,  Soup initialize for deeper crawling one level
		bSoup = BeautifulSoup(urllib2.urlopen(eventURL))
		
		#BreadCrums SFGate Specific Data
		sfGateBreadcrumb= bSoup.find('span', attrs = {'itemprop':'breadcrumb'}).findAll('a')[-1]  #Gets a list of all the Breadcrumbs <a href> and takes last one [-1]
	
		#Event Name   Generic
		eventTitle 		= bSoup.find('span', attrs = {'class':'summary'}).contents[0]
		
		#Parsing Time Generic
		try:	eventStartDateTime = str(bSoup.find('abbr', attrs = {'class':'dtstart'}).attrs['title']).replace("T"," ").replace("Z", " ")
		except:	eventStartDateTime=""
		#eventStartDate	= startTime[:startTime.find("T")]
		#eventStartTime	= startTime[startTime.find("T")+1:startTime.find("Z")]
		try:	eventTimeRaw       = bSoup.find('abbr', attrs = {'class':'dtstart'}).contents[0]
		except:	eventTimeRaw = ""

		#Venue Info   Generic
		venue 			= bSoup.find('div', attrs = {'class':'venue'}).next_element.next_element
		venueID			= venue.attrs['data-z-destination-venue-id']
		#venueURL		= venue.attrs['href']
		venueName		= venue.contents[0]

		#Event Description  Generic
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
			eventDescription = excerpt
		except:	eventDescription = ""
		
		try:	eventWebsite	= str(bSoup.find('div', attrs = {'class' : 'detail'}).next_element.next_element.attrs['href'])
		except:	eventWebsite = ""
		try:	eventPhone	= str(bSoup.find_all('span', attrs = {'class':'title'},text="Phone")[0].next_sibling.string)
		except:	eventPhone = ""
		try:	eventPrice		= bSoup.find_all('span', attrs = {'class':'title'},text="Price")[0].next_sibling.string
		except: eventPrice = ""
		try:	ageSuitability 	= bSoup.find_all('span', attrs = {'class':'title'},text="Age Suitability")[0].next_sibling.string
		except:	ageSuitability = ""
		
		#Adress Generic
		try:	addressStreet 		= bSoup.find('span', attrs = {'class':'street-address'}).contents[0]
		except:	addressStreet = ""
		try:	addressLocality		= bSoup.find('span', attrs = {'class':'locality'}).contents[0]
		except:	addressLocality = ""
		try:	addressRegion		= bSoup.find('span', attrs = {'class':'region'}).contents[0]
		except:	addressRegion=""
		try:	addressPostalCode= bSoup.find('span', attrs = {'class':'postal-code'}).contents[0]
		except:	addressPostalCode=""
		
		
		#SFGATE Get Image URL, and Creator of Event
		try:	sfGateImageURL 	= bSoup.find('div' , attrs = {'class':'main_image'}).next_element.next_element.attrs['src']
		except:	sfGateImageURL=""
		try:	sfGateCreator   		= bSoup.find('strong',text="Creator:").parent.find('a').text
		except:	sfGateCreator=""

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
		#sfGateTags = ""
		#tagsRaw = bSoup.find_all('span', attrs = {'id':'taglist'})[0].findAll('a')
		#for tag in tagsRaw:
		#	if sfGateTags == "":	sfGateTags = str(tag.text)
		#	else:	sfGateTags = str(sfGateTags) + "," + str(tag.text)
				
		#Write to Couchbase Create JSON Document
		newEvent = \
		{
			"jsonType":				"Event",
			"eventTitle": 			eventTitle,
			"eventStartDateTime":	eventStartDateTime,
			"eventTimeRaw":			eventTimeRaw,
			"venueName":			venueName,
			"eventDescription":		eventDescription,
			"eventWebsite":			eventWebsite,
			"eventPhone":			str(eventPhone),
			"eventPrice":			eventPrice,
			"ageSuitability":		str(ageSuitability),
			"addressStreet":		addressStreet,
			"addressLocality":		addressLocality,
			"addressRegion"	:		addressRegion,
			"addressPostalCode":	addressPostalCode
		}
		
		try:	bucket[getKey(str(eventTitle.encode("utf-8")))] = json.dumps(newEvent)  #UUID is hex of eventTitle
		except: print "Failed to Connect"
	# Pickup Next Page, return url so crawler can crawl next page
	try:	nextPage = "http://events.sfgate.com"+str(soup.find('div',attrs={"class":"pager"}).find('a').attrs['href'])
	except:	nextPage = 0
	return nextPage

url = "http://events.sfgate.com/search?srad=85.0&swhat=&swhen=Next+30+Days&swhere=San+Francisco%2C+CA&st=event&new=n&srss=50"

while url !=0:
	print url
	url = crawlSFGate(url)




