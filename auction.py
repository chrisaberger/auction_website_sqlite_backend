#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from sql_page import sql_page

class auction(sql_page):
    def GET(self):
        post_params = web.input()
        try:
            itemID = int(post_params['id'])
        except:
            return self.render_template('auction.html')

        return self.getNotOverloaded(itemID,'')
        #get item information
        #if no item lookup display basic template
    def getNotOverloaded(self,itemID,message):
        t = sqlitedb.transaction()
        try:
            bidClosed = sqlitedb.isAuctionClosed(itemID)
            itemResults = sqlitedb.getAuctionByItemID(itemID)
            itemInfo = self.prepareQueryForRender(itemResults)
            categoryResults = sqlitedb.getAuctionCategories(itemID)
            sellerResults = sqlitedb.filterBySeller( ((itemInfo['rows'])[0]['sellerID']) )
            bidResults = sqlitedb.getBidHistory(itemID)
            winner = sqlitedb.auctionWinner(itemID)
        except Exception as e:
            print(e)
        else:
            t.commit()

        categoryInfo = self.prepareQueryForRender(categoryResults) 
        sellerInfo = self.prepareQueryForRender(sellerResults)
        bidInfo = self.prepareQueryForRender(bidResults)
        try: 
            winner = winner[0]['bidderID']
        except:
            winner='Nobody'
        itemInfo.update(\
            {'bidClosed':bidClosed,\
            'winner':winner,\
            'description':(itemInfo['rows'])[0]['description']})
        #overwrite the item cols because the order gets randomly changed
        itemInfo['cols'] = ['itemID','name','currently','buyPrice','numberOfBids','started','ends','sellerID','firstBid']        
        return self.render_template('auction.html', \
            itemInfo = itemInfo,\
            categoryInfo = categoryInfo,\
            bidInfo = bidInfo,\
            message = message,\
            sellerInfo = sellerInfo)
        
    def POST(self):
    	return getInputArgsThenQuery()

    def getInputArgsThenQuery():
    	post_params = web.input()
        message = ''
        itemid = int(post_params['itemid'])
        try:
            itemid = int(post_params['itemid'])
        except:
            message = 'Bad entry: you must enter a valid item id!'
            return self.render_template('auction.html',message=message)
        userid = post_params['userid']
        if(userid==''):
            message = 'Bad entry you must enter your user id!'
            return self.render_template('auction.html',message=message)
        try:
            price = float(post_params['price'])
        except:
            message = 'Bad entry: you must enter a valid price!'
            return self.render_template('auction.html',message=message)
     	return querySearchArgs(message,itemid,userid,price)

    def querySearchArgs(message,itemid,userid,price):
    	t = sqlitedb.transaction()
        try:
            bidClosed = sqlitedb.isAuctionClosed(itemid)
            if bidClosed:
                message = "Bid not placed! I'm sory the auction is closed for item id:" + str(itemid)
                return self.getNotOverloaded(itemid,message)
            currentTime = sqlitedb.getTime()
            sqlitedb.placeBid(currentTime,itemid,userid,price)
            sqlitedb.updateNumberOfBidsAndCurrently(itemid,price)
        except Exception as e:
            t.rollback()
            message = "Bid not placed! " + str(e)
            if str(e)=='constraint failed':
                message = "Bid not placed! You wagered more than the buy price. Just trying to save you money!"
            if str(e)=='foreign key constraint failed':
                message = "Bid not placed!  User " + userid + " does not exist!"
            return self.getNotOverloaded(itemid,message)
        else:
            t.commit()

        message = userid + ' successfully placed a bid of $' + str(price) +' itemID=' + str(itemid)
        return self.getNotOverloaded(itemid,message)


