#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/search_auctions', 'search_auctions',
        # TODO: add additional URLs here
        '/auction','auction'
        #'/auction?id=(.+)','auctionWithID'
        # first parameter => URL, second parameter => class name
        )

class sql_page:
    def prepareQueryForRender(self,result):
        inRows = result.list()
        inCols = []
        if inRows:
            inCols = inRows[0].keys()
        return inRows,inCols

class auction(sql_page):
    def GET(self):
        post_params = web.input()
        if(post_params):
            #get item information
            itemID = int(post_params['id'])
            itemResults,categoryResults = sqlitedb.filterByItemId(itemID)
            itemRows,itemCols = self.prepareQueryForRender(itemResults)
            description = itemRows[0]['description']
            categoryRows,categoryCols = self.prepareQueryForRender(categoryResults) 
    
            bidClosed = sqlitedb.isAuctionClosed(itemID)
            print("bidClosed : %b ", bidClosed)
            sellerID = itemRows[0]['sellerID'] 
            sellerQuery = sqlitedb.filterBySeller(sellerID)
            sellerRows,sellerCols = self.prepareQueryForRender(sellerQuery)
        
            bidResults = sqlitedb.getBidHistory(itemID)
            bidRows,bidCols = self.prepareQueryForRender(bidResults)
        
            winner = sqlitedb.auctionWinner(itemID)        
            try: 
                winnerIn = winner[0]['bidderID']
            except:
                winnerIn='Nobody'
                    
            return render_template('auction.html', \
                itemRows = itemRows, itemCols = itemCols, description=description, \
                categoryRows = categoryRows, categoryCols = categoryCols, \
                sellerRows = sellerRows, sellerCols = sellerCols, winner = winnerIn, \
                bidRows = bidRows, bidCols=bidCols, bidClosed = bidClosed)
        return render_template('auction.html')
    def POST(self):
        return render_template('auction.html')

class search_auctions(sql_page):
    def GET(self):
        return render_template('search_auctions.html')
    def POST(self):
        post_params = web.input()
        bidStatus = post_params['bid_status']
        if bidStatus=='closed':
            bidStatus='and Date(currentTime)>=Date(ends)'
        elif bidStatus=='open':
            bidStatus='and Date(currentTime)<Date(ends)'
        else:
            bidStatus=' order by currently'

        name = post_params['name']
        if name != '':
            name = ' and name like \'%' + name + '%\' '
         
        try:
            itemID = int(post_params['itemid'])
        except:
            itemID = None
        try:
            priceHigh = float(post_params['toPrice'])
        except: 
            priceHigh = None
        try:
            priceLow = float(post_params['fromPrice']) 
        except:
            priceLow = 0
        try:
            category = '%' + post_params['category'] + '%'
            if(category=='%%'):
                raise Exception("No value for category")
        except:
            category = None
        
        if itemID is not None:
            return self.displayByItemID(itemID,name,bidStatus)
        elif category is not None and priceHigh is not None:
            return self.displayByPriceAndCategory(category,priceLow,priceHigh,name,bidStatus)
        elif category is not None and priceHigh is None:
            return self.displayByCategory(category,priceLow,name,bidStatus)
        elif priceHigh is not None:
            return self.displayByPrice(priceHigh,priceLow,name,bidStatus)
        else:
            return self.displayByStatus(priceLow,name,bidStatus)
             #if(bidClosed and bidStatus=='Open'):
            #    raise Exception("Search produced only a closed bid")
        #except:   itemResults,categoryResults = sqlitedb.filterByItemId(itemID)
        #    itemRows,itemCols = self.prepareQueryForRender(itemResults)
        #    catRows, catCols = self.prepareQueryForRender(categoryResults)
        #    bidClosed = sqlitedb.isAuctionClosed('itemID')

    def displayByItemID(self,itemID,name,bidStatus):
        itemResults = sqlitedb.filterByItemIDSimple(itemID,name,bidStatus)
        itemRows,itemCols = self.prepareQueryForRender(itemResults)
        message = ''
        if itemRows==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemRows = itemRows, itemCols = itemCols, message=message) \
    
    def displayByPriceAndCategory(self,category,priceLow,priceHigh,name,bidStatus):
        itemResults = sqlitedb.filterByPriceAndCategory(category,priceLow,priceHigh,name,bidStatus)
        itemRows,itemCols = self.prepareQueryForRender(itemResults)
        message = ''
        if itemRows==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemRows = itemRows, itemCols = itemCols, message=message) \
    
    def displayByCategory(self,category,priceLow,name,bidStatus):
        itemResults = sqlitedb.filterByCategory(category,priceLow,name,bidStatus)
        itemRows,itemCols = self.prepareQueryForRender(itemResults)
        message = ''
        if itemRows==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemRows = itemRows, itemCols = itemCols, message=message) \
 
    def displayByPrice(self,priceHigh,priceLow,name,bidStatus):
        itemResults = sqlitedb.filterByPrice(priceHigh,priceLow,name,bidStatus)
        itemRows,itemCols = self.prepareQueryForRender(itemResults)
        message = '' 
        if itemRows==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemRows = itemRows, itemCols = itemCols, message=message)
         
    def displayByStatus(self,priceLow,name,bidStatus):
        itemResults = sqlitedb.filterByBidStatus(priceLow,name,bidStatus)
        itemRows,itemCols = self.prepareQueryForRender(itemResults)
        message = ''
        if itemRows==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemRows = itemRows, itemCols = itemCols, message=message)
       

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        try:
            sqlitedb.updateTime(selected_time)
        except:
            update_message = 'ERROR: Time was not adjusted.  Remember you cannot go back in time...duh!'
        
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.run()
