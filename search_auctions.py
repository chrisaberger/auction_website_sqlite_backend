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
        bidStatus = post_params['bid_status']
        if bidStatus=='closed':
            bidStatus=' Datetime(currentTime)>=Datetime(ends) '
        elif bidStatus=='open':
            bidStatus=' Datetime(currentTime)<Date(ends) '
        else:
            bidStatus=' Datetime(currentTime)=Datetime(currentTime)'
        #how to order the search results for display
        order = post_params['sort_by']
        if order=='price':
            order= ' order by currently '
        elif order=='endTime':
            order= ' order by ends '
        else:
            order=' order by numberOfBids'
        #category:string to filter category names on
        #need a seperate query b/c schema has it in seperate table
        category = post_params['category']
        if category != '':
            category = ' and categoryName like \'%' + category + '%\''

        #name:string to filter name, directly appended to queries
        name = post_params['name']
        if name != '':
            name = ' and name like \'%' + name + '%\' '

        message = ''
        #itemID: query string
        itemID = post_params['itemid']
        if itemID != '':
            try:
                itemID = int(itemID)
                itemID = ' and itemID=' + str(itemID) + ' '
            except:
                itemID = ''
                message += 'Error: ITEM ID entered was not of proper type (Integer) -> filter ignored. '
        #priceHigh: query string
        priceHigh = post_params['toPrice']
        if priceHigh != '':
            try:
                priceHigh = float(priceHigh)
                priceHigh = ' and currently<=' + str(priceHigh) + ' '
            except: 
                priceHigh = ''
                message += 'Error: TO PRICE entered was not of proper type (Number) -> filter ignored. '
        #priceLow: query string
        priceLow = post_params['fromPrice']
        if priceLow != '':
            try:
                priceLow = float(priceLow)
                priceLow = ' and currently>=' + str(priceLow) + ' '
            except: 
                priceLow = ''
                print("Ooooooooooooooo")
                message += 'Error: FROM PRICE entered was not of proper type (Number) -> filter ignored. '

        return {'bidStatus':bidStatus,\
            'name':name,\
            'itemID':itemID,\
            'priceHigh':priceHigh,\
            'priceLow':priceLow,\
            'order':order,\
            'message':message,\
            'category':category}

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
