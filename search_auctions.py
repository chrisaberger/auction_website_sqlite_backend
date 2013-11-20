#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from sql_page import sql_page

class search_auctions(sql_page):
    def GET(self):
        itemInfo = {'rows':[],'cols':[]}
        return self.render_template('search_auctions.html')
    def POST(self):
        search_params = self.getSearchParameters()
        return self.displaySearch(search_params)

    def getSearchParameters(self):
        #this method is ugly ugghhhhh
        #grab input
        post_params = web.input()
        #bid status: open,closed or any
        #must come as first term in search query
        #last case does nothing just a way to get syntax with AND's in others to work
        bidStatus = self.getBidStatus(post_params['bid_status'])
        #how to order the search results for display
        order = self.getOrder(post_params['sort_by'])
        #category:string to filter category names on
        #need a seperate query b/c schema has it in seperate table
        category = self.getCategory(post_params['category'])
        #name:string to filter name, directly appended to queries
        name = self.getName(post_params['name'])
        #itemID: query string
        (itemID,message) = self.getItemID(post_params['itemid'],'')
        #priceHigh: query string
        (priceHigh,message) = self.getPriceHigh(post_params['toPrice'],message)
        #priceLow: query string
        (priceLow,message) = self.getPriceLow(post_params['fromPrice'],message)
        
        return {'bidStatus':bidStatus,\
            'name':name,\
            'itemID':itemID,\
            'priceHigh':priceHigh,\
            'priceLow':priceLow,\
            'order':order,\
            'message':message,\
            'category':category}
    def getBidStatus(self,bidStatus):
        if bidStatus=='closed':
            bidStatus=' Datetime(currentTime)>=Datetime(ends) or (currently>=buyPrice and buyPrice is not null) '
        elif bidStatus=='open':
            bidStatus=' Datetime(currentTime)<Date(ends) and (currently<buyPrice or buyPrice is null)'
        else:
            bidStatus=' Datetime(currentTime)=Datetime(currentTime)'
        return bidStatus
    def getOrder(self,order):
        if order=='price':
            order= ' order by currently '
        elif order=='endTime':
            order= ' order by ends '
        else:
            order=' order by numberOfBids'
        return order
    def getCategory(self,category):
        if category != '':
            category = ' and categoryName like \'%' + category + '%\''
        return category
    def getName(self,name):
        if name != '':
            name = ' and name like \'%' + name + '%\' '
        return name
    def getItemID(self,itemID,message):
        if itemID != '':
            try:
                itemID = int(itemID)
                itemID = ' and itemID=' + str(itemID) + ' '
            except:
                itemID = ''
                message += 'Error: ITEM ID entered was not of proper type (Integer) -> filter ignored. '
        return (itemID,message)
    def getPriceHigh(self,priceHigh,message):
        if priceHigh != '':
            try:
                priceHigh = float(priceHigh)
                priceHigh = ' and currently<=' + str(priceHigh) + ' '
            except: 
                priceHigh = ''
                message += 'Error: TO PRICE entered was not of proper type (Number) -> filter ignored. '
        return (priceHigh,message)
    def getPriceLow(self,priceLow,message):
        if priceLow != '':
            try:
                priceLow = float(priceLow)
                priceLow = ' and currently>=' + str(priceLow) + ' '
            except: 
                priceLow = ''
                message += 'Error: FROM PRICE entered was not of proper type (Number) -> filter ignored. '
        return (priceLow,message)
    def displaySearch(self,search_params):
        if search_params['category']=='':
            itemResults = sqlitedb.filterOnItemRelation(search_params)
        else:
            itemResults = sqlitedb.filterOnItemAndCategoryRelation(search_params)
        itemInfo = self.prepareQueryForRender(itemResults)
        #overwrite the item cols because the order gets randomly changed
        itemInfo['cols'] = ['itemID','name','currently','buyPrice','numberOfBids','started','ends']
        message = search_params['message']
        if itemInfo['rows']==[] and message=='':
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return self.render_template('search_auctions.html', \
            itemInfo = itemInfo,\
            message=message)   
