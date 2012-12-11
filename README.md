sfGateCrawler
=============
Crawler goes to SFGate.com and crawls events that occur within 30 days. Currently, only generic info of the event is stored into a Couchbase Server (i.e. eventTitle, eventDescription, eventAddress).

There are other items crawled that are specific to SFGATE.com, such as sfGateEventID which is unique for each event-these are not stored in the Couchbase

 
Crawls SF Gate

Generic event Info 
eventTitle		STR: Name of Event
eventStartDateTime	STR: Format 2012-12-14   YYYY-MM-DD

venueName		STR: Venue Name
eventDescription	STR: Description of Event
eventWebsite		STR: eventWebsite
eventPhone		STR: event Phone Number
eventPrice		STR: Description of Prices – Not formatted
ageSuitability		STR: Age Suitability – Not formatted
addressStreet		STR: Address Street 
addressLocality		STR: Locality/City
addressRegion		STR: Region/State
addressPostalCode	STR: Postal Code

Unique info from SFGATE.com Website
sfGateEventID		INT: ID that SFgate uses to store their event
sfGateEventRank	INT: Ranking of display at time of crawl
sfGateEventSponsored	BOOL: 0 or 1 is this a “sponsored/paid” event on sf gate
sfGateEventCanceled	BOOL: 0 or 1, is the event canceled
sfGateBreadcrum	STR: Breadcrumb to determine 
sfGateVenueID		INT: Sf gate’s proprietary VenueID
sfGateImageURL	STR: Url of image displayed on page for event
sfGateCreator		STR: Name of organizer creating event
sfGateCategory		STR: Format “Category1,Category2,Category3”
sfGateTags		STR: Format “Tag1,Tag2”  Tags from website
