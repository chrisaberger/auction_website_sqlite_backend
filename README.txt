Christopher R. Aberger
CS 145: Project Part 3

1. HOW TO LOCATE BASIC CAPABILITIES    
    cgi-bin/auctionbase.py/currtime
        -Displays the current time for auction database
    cgi-bin/auctionbase.py/selecttime
        -Allows user to manually change the time
        -You cannot go back in time
        -Displays the current time
    cgi-bin/auctionbase.py/search_auctions
        -Allows user to browse all auctions based upon
        input paramters described in step 2.
    cgi-bin/auctionbase.py/auction
        -You can get here 1 of two ways
            a. click tab atop all pages
                -here you can place a bid for any item or itemID
            b. after browsing auctions (in search_auctions)
            hyperlinks are placed on each itemID that meets search criteria
                -Will display open or closed for item you can off link from
                -If open allows you to place a bid
        -No matter if item is open or closed for item you try to 
        bid on you will get all the information for that item including
        whether it is opened or closed on this page
        -Can never place a bid for a closed item, system can handle any 
        input and will gracefully display errors to user

2. INPUT PARAMETERS        
        -System gracefully handles any input and displays useful hints
        to user if something is wrong with input parameters.
        -List of parameters
            a. Search by bid status: open, closed, any
            b. Sort by (ascending order always): Price, Number of Bids, End Time
            c. Item Id
            d. Item name: matches any name that contains your input string
            e. Item category: matches any category that contains your string
            f. Price Range: type checks to make sure it is a number,
                if just from or to price is entered uses that as a 
                respective floor.
        -System handles and matches and all combinations of paramters a-e 
        entered. 
            *Meaning if you enter an item name and price range it will search
            based upon both criteria (does this for all inputs).

3. EXTRA
    -My system gracefully handles all input and displays
    useful error messages that go above and beyond what is required.
    -Hyperlinking between item id and auction page.

