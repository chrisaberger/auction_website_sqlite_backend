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
        '/auction','auction'
        )

class sql_page:
    def prepareQueryForRender(self,result):
        inRows = result.list()
        inCols = []
        if inRows:
            inCols = inRows[0].keys()
        return {'rows':inRows,'cols':inCols}

class auction(sql_page):
    def GET(self):
        post_params = web.input()
        try:
            itemID = int(post_params['id'])
        except:
            return render_template('auction.html')

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
        return render_template('auction.html', \
            itemInfo = itemInfo,\
            categoryInfo = categoryInfo,\
            bidInfo = bidInfo,\
            message = message,\
            sellerInfo = sellerInfo)
        
    def POST(self):
        post_params = web.input()
        message = ''
        itemid = int(post_params['itemid'])
        try:
            itemid = int(post_params['itemid'])
        except:
            message = 'Bad entry: you must enter a valid item id!'
            return render_template('auction.html',message=message)
        userid = post_params['userid']
        if(userid==''):
            message = 'Bad entry you must enter your user id!'
            return render_template('auction.html',message=message)
        try:
            price = float(post_params['price'])
        except:
            message = 'Bad entry: you must enter a valid price!'
            return render_template('auction.html',message=message)

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

class search_auctions(sql_page):
    def GET(self):
        itemInfo = {'rows':[],'cols':[]}
        return render_template('search_auctions.html')
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
        category = ' and categoryName like \'%' + post_params['category'] + '%\''
        if(category=='%%'):
            category = None 
        #name:string to filter name, directly appended to queries
        name = post_params['name']
        if name != '':
            name = ' and name like \'%' + name + '%\' '
        #itemID: query string
        try:
            itemID = ' and itemID=' + int(post_params['itemid']) + ' '
        except:
            itemID = ''
        #priceHigh: query string
        try:
            priceHigh = ' and currently<=' + float(post_params['toPrice']) + ' '
        except: 
            priceHigh = ''
        #priceLow: query string
        try:
            priceLow = ' and currently>=' + float(post_params['fromPrice']) + ' '
        except:
            priceLow = ''

        return {'bidStatus':bidStatus,\
            'name':name,\
            'itemID':itemID,\
            'priceHigh':priceHigh,\
            'priceLow':priceLow,\
            'order':order,\
            'category':category}

    def displaySearch(self,search_params):
        if search_params['category']=='':
            itemResults = sqlitedb.filterOnItemRelation(search_params)
        else:
            itemResults = sqlitedb.filterOnItemAndCategoryRelation(search_params)
        itemInfo = self.prepareQueryForRender(itemResults)
        #overwrite the item cols because the order gets randomly changed
        itemInfo['cols'] = ['itemID','name','currently','buyPrice','numberOfBids','started','ends']
        message = ''
        if itemInfo['rows']==[]:
            message = "I'm sorry nothing met your search criteria. Please try a more general option."
        return render_template('search_auctions.html', \
            itemInfo = itemInfo,\
            message=message)   

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
        current_time = sqlitedb.getTime()
        return render_template('select_time.html', time = current_time)

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
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
