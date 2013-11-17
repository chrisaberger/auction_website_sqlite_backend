import web

db = web.database(dbn='sqlite',
        db='auctions.db' #TODO: add your SQLite database filename
    )
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

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
def getCurrentTime():
    query_string = 'select currentTime from Time'
    currentTime = query(query_string)
    return currentTime

def placeBid(currentTime,itemid,userid,price):
    query_string = 'insert into Bid values ($ct,$bid,$p,$iid)'
    query(query_string,{'iid':itemid,'ct':currentTime,'p':price,'bid':userid})
    return 

def updateNumberOfBidsAndCurrently(itemid,price):
    query_string = 'update Item set numberOfBids=numberOfBids+1,currently=$p where itemID=$iid'
    query(query_string,{'iid':itemid,'p':price})
    return 

def auctionWinner(itemID):
    query_string = 'select distinct bidderID from Bid where itemID=$id group by itemID having max(amount)'
    winnerID = query(query_string,{'id':itemID})
    return winnerID

def filterOnItemRelation(search_params):
    query_string = 'select distinct itemID,name,currently,numberOfBids,started,ends,buyPrice from Item join Time where ' \
        + search_params['bidStatus']\
        + search_params['name']\
        + search_params['itemID']\
        + search_params['priceHigh']\
        + search_params['priceLow']\
        + search_params['order']
    item_results = query(query_string)
    return item_results

def filterOnItemAndCategoryRelation(search_params):
    query_string = 'select distinct itemID,name,currently,numberOfBids,started,ends,buyPrice from (Item join Category using(itemID)) join Time where ' \
        + search_params['bidStatus']\
        + search_params['name']\
        + search_params['itemID']\
        + search_params['priceHigh']\
        + search_params['priceLow']\
        + search_params['category']\
        + search_params['order']
    item_results =query(query_string)
    return item_results

def isAuctionClosed(itemID):
    query_string = 'select * from Item join Time where itemID=$id and (currently<buyPrice or buyPrice is null) and Datetime(currentTime)<Datetime(ends)'
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

def getAuctionByItemID(item_id):
    query_string = 'select * from Item where itemID=$id'
    item_results =query(query_string,{'id': item_id})
    return item_results
 
def getAuctionCategories(item_id):
    query_string = 'select categoryName as Categories from Category where itemID=$id'
    category_results = query(query_string,{'id': item_id})
    return category_results

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
