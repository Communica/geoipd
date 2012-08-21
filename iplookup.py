#!/usr/bin/env python
#coding: utf-8
#
#
#	Geo-ip loookup based on the database provided by: http://software77.net/geo-ip/
#	To fetch the latest version of the db:
#	
#		 wget software77.net/geo-ip/?DL=1 -O /path/IpToCountry.csv.gz      IPV4 gzip	
#
#	OR:
#
# 		 wget software77.net/geo-ip/?DL=2 -O /path/IpToCountry.csv.zip     IPV4 zip	
#
#	Locally cached db.
#
# @author: technocake
# @changelog:
#	when	who			what
#	210812	technocake	made alpha version, capable of lookups.
#
##########################################################################################
import csv, math, sys, re, socket

db = []	# db in memory.


def ip2dec(ipv4):
	""" Converts ip from dotted decimal notation to decimal notation:
		Example:  158.37.91.42 --> 2653248298
	"""
	dec = 0
	for i, octett in enumerate(ipv4.split('.')[::-1]):
		dec += (256**i) * int(octett)
	return dec



def iprange2net(fromip, toip):
	""" Takes in a ip range (in decimal form)
		Returns a tuple of network and mask in CIDR notation
		"""
	#Dirty assumption here!
	net = fromip 
	mask = int( 32 - math.log( (toip - fromip) + 1,   2 ) )
	return (net, mask) 



class CommentedFile:
    def __init__(self, f, commentstring="#"):
    	""" Helper-class for parsing commented csv files. 
	  	@see: http://www.mfasold.net/blog/2010/02/python-recipe-read-csvtsv-textfiles-and-ignore-comment-lines/ 
	  	"""
        self.f = f
        self.commentstring = commentstring
    def next(self):
        line = self.f.next()
        while line.startswith(self.commentstring):
            line = self.f.next()
        return line
    def __iter__(self):
        return self




def parseIpDB(dbfile='IpToCountry.csv'):
	"""		Loads the geo-ip csv-file into memory. 		"""
	global db
	ipreader = csv.reader(
		CommentedFile(
			open(dbfile, 'rb'),
		 	'#'
		) 	
	)
	
	#ipfrom, ipto, reg, date, ctr,cntr,country
	for row in ipreader:
		db.append(row)
	

def lookup(ipv4):
	""" Lookup function  ipv4 --> ipfrom, ipto, reg, date, ctr,cntr,country """
	global db
	ipv4 = socket.gethostbyname(ipv4)
	#Converting to decimal formated ip
	ip = ip2dec(ipv4)
	
	#ipfrom, ipto, reg, date, ctr,cntr,country
	for row in db:
		if int(row[1]) < ip: continue
		else: return row


def lookup_ctr(ipv4):
	""" Lookup function:   ipv4 --> country code
		Example: 	
			lookup_ctr('158.37.91.42') --> NO 
	"""
	#ipfrom, ipto, reg, date, ctr,cntr,country
	return lookup(ipv4)[4]

#tests
if __name__ == '__main__':
	parseIpDB()
	print lookup_ctr('158.37.91.42')
	print ip2dec('158.37.91.42')
