import web

db = web.database(dbn='sqlite',
        db='auctions.db' #TODO: add your SQLite database filename
    )
db.query('PRAGMA foreign_keys = ON') # Enable foreign key constraints
                                     # WARNING: DO NOT REMOVE THIS!

######################BEGIN HELPER METHODS######################

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except:
#     t.rollback()
#     raise
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples
def auctionWinner(itemID):
    query_string = 'select bidderID from Bid where itemID=$id group by itemID having max(amount)'
    item_results =query(query_string,{'id':itemID})
    return item_results

def filterByItemIDSimple(item_id,name,bidStatus):
    query_string = 'select * from Item where itemID=$id' + name + bidStatus
    item_results =query(query_string,{'id': item_id})
    return item_results
 
def filterByPriceAndCategory(category,priceLow,priceHigh,name,bidStatus):
    query_string = 'select distinct itemID,name,currently,ends,numberOfBids from (Item join Category using(itemID)) join Time where currently>=$pl and currently<=$ph and categoryName like $ct ' + name + bidStatus
    item_results =query(query_string,{'pl':priceLow,'ph':priceHigh,'ct':category})
    return item_results

def filterByCategory(category,priceLow,name,bidStatus):
    query_string = 'select distinct itemID,name,currently,ends,numberOfBids from (Item join Category using(itemID)) join Time where currently>=$pl and categoryName like $ct ' + name + bidStatus
    item_results =query(query_string,{'pl':priceLow,'ct':category})
    return item_results

def filterByBidStatus(low,name,bidStatus):
    query_string = 'select distinct itemID,name,currently,ends,numberOfBids from Item join Time where currently>=$l' + name + bidStatus 
    item_results =query(query_string,{'l':low})
    return item_results

def filterByPrice(high,low,name,bidStatus):
    query_string = 'select * from Item join Time where currently<=$h and currently>=$l ' + name + bidStatus
    results = query(query_string,{'h':high,'l':low})
    return results 

def isAuctionClosed(itemID):
    query_string = 'select * from Item join Time where itemID=$id and Date(currentTime)<=Date(ends)'
    results = query(query_string,{'id':itemID})
    return isResultEmpty(results) 

def getBidHistory(itemID):
    query_string = 'select * from Bid where itemID=$id order by time'
    results = query(query_string,{'id':itemID})
    return results

def filterBySeller(seller_id):
    query_string = 'select * from User where userID=$id'
    results = query(query_string,{'id':seller_id})
    return results

def filterByItemId(item_id):
    query_string = 'select * from Item where itemID=$id'
    item_results =query(query_string,{'id': item_id})
 
    query_string = 'select categoryName as Categories from Category where itemID=$id'
    category_results = query(query_string,{'id': item_id})
    
    return item_results, category_results

def updateTime(new_time):
    query_string = 'update Time set currentTime= $nt'
    query(query_string,{'nt': new_time}) 
    return 

# returns the current time from your database
def getTime():
    query_string = 'select currentTime from Time'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].currentTime # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where item_ID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

# helper method to determine whether query result is empty
# Sample use:
# query_result = sqlitedb.query('select currenttime from Time')
# if (sqlitedb.isResultEmpty(query_result)):
#   print 'No results found'
# else:
#   .....
#
# NOTE: this will consume the first row in the table of results,
# which means that data will no longer be available to you.
# You must re-query in order to retrieve the full table of results
def isResultEmpty(result):
    try:
        result[0]
        return False
    except:
        return True

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return db.query(query_string, vars)

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
