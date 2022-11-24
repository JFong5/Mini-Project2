import re

import pymongo
from pymongo import MongoClient

def inputPortNum():
    '''
    Prompts the user for a Port Num
    Return: Port Num Input (Int)
    '''
    portNum = int(input("Please input a port number. \n"))
    print("")
    return portNum


def mainMenu(db):
    '''
    Prompts user for an option from 1 to 5
    Execute certain functions for each choice 
    '''
    #Prompt user for option number
    choice = int(input("Please select the following task you would like to perform: \n1.Search for article \n2.Search for authors \n3.List the venues \n4.Add an article \n5.Exit \n"))
    if choice == 1:
        #Executes searchForArticle(db) function
        print("")
        searchForArticle(db)
    elif choice == 2:
        #Executes searchForAuthors(db) function
        print("")
        searchForAuthors(db)
    elif choice == 3:
        #Executes listVenues(db) function
        print("")
        listVenues(db)
    elif choice == 4:
        #Executes addArticle(db) function
        print("")
        addArticle(db)
    elif choice == 5:
        #Executes exit function and closes program
        print("")
        exit()

def searchForArticle(db):
    """
    Prompts user for keyword
    Displays all Articles matching the keyword
    """ 
    collection = db["dplb"]

    def getKeyArticle(articleItem, key):
        """
        Given an article and a key, return the value of the key
        """
        if key in articleItem:
            return articleItem[key]
        else:
            return None
    def printArticle(articleItem):
        """
        Given an article, print all the fields
        Check for references and print them
        """
        print(f"\nid: {getKeyArticle(articleItem, 'id')}")
        print(f"title: {getKeyArticle(articleItem, 'title')}")
        print(f"year: {getKeyArticle(articleItem, 'year')}")
        print(f"venue: {getKeyArticle(articleItem, 'venue')}")
        print(f"# of citations: {getKeyArticle(articleItem, 'n_citation')}")
        print(f"authors: {', '.join(map(str, getKeyArticle(articleItem, 'authors')))}")
        print(f"abstract: {getKeyArticle(articleItem, 'abstract')}")\
        
        if getKeyArticle(articleItem, 'references') != None:
            print("References:")
            references = getKeyArticle(articleItem, 'references')
            for reference in references:
                print(f"\t{reference}")
                results = collection.find({"id": {"$in": [reference]}})
                referenceArticle = results

                for article in referenceArticle:
                    print(f"\t\tid: {getKeyArticle(article, 'id')}")
                    print(f"\t\ttitle: {getKeyArticle(article, 'title')}")
                    print(f"\t\tyear: {getKeyArticle(article, 'year')}")
        else:
            
            print("References: None")
    
    userInput = input("Please insert a keyword or keywords of the article you would like to search\n")
    keywordsList = userInput.split()
    keywords = ""
    print("")

    for word in keywordsList:
        keywords += f"\"{word}\" "

    articles = collection.find({"$text": {"$search": keywords}})
    articleDict = dict((x, article) for x, article in enumerate(articles, 1))
   
    print("The search returned " + str(len(articleDict)) + " articles:")
    for key, value in articleDict.items():
        print(f"{key}. | {value['title']} | {value['year']} | {value['venue']}")
    
    #checks
    if len(articleDict) == 0:
        print("0 results found")
        print("")
    else:
        userSelection = input("Please select an article to see all fields including the abstract and the authors in addition to the fields listed above. \n")
        while userSelection.isdigit() == False or int(userSelection) <= 0 or int(userSelection) > (len(articleDict)):
            userSelection = (input("Invalid selection! Please select a valid option.\n"))
    
        userSelection = int(userSelection)
        while userSelection < 1 and userSelection > (len(articleDict) + 1):
            userSelection = int(input("Please select a valid option. \n"))
        #print all the articles
        printArticle(articleDict[userSelection])
    print("")

    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        print("")
        mainMenu(db)
    elif userChoice == 2:
        exit()

def searchForAuthors(db):
    '''
    Prompts user for a keyword
    Displays all authors whose names contain the keyword, displays author name and the number of publications
    '''
    
    #Creates Collection
    collection = db["dplb"]

    #Prompts user for a keyword
    keyword = input("Please enter a keyword to search for authors: ")
    #words += (keyword + " ")

    #query to find items in collection with common author names
    query = {"authors" : {"$in": [re.compile(r"(?i)" + keyword)]}}

    #Executes Query *Need to test if query uses indexes
    executeQuery = collection.find(query)

    #Aggregate results

    #Format the output of the query
    #append all authorname arrays in authorNames
    authorNames = []
    for dic in executeQuery:
        for key in dic:
            if key == "authors":
                authorNames.append(dic[key])
    

    #Gather all matchingNames from query and append to list
    matchingNames = []
    matchingNamesDic = {}
    for names in authorNames:
        for name in names:
            if keyword.lower() in name.lower():
                matchingNames.append(name)

    
    #Check to see how many times the name appears in the list and it publication number is the value
    for name in matchingNames:
        matchingNamesDic[name] = 0
    
    for name in matchingNames:
        matchingNamesDic[name] += 1

    #Prints the name and number of publications
    n = 0
    for k in matchingNamesDic:
        n = n+1
        print(str(n) + ": " + '{:15s} {:4}'.format(k,str(matchingNamesDic[k])))
    print("")

    #Checks if there are any matching author names
    #Prompts the user to select which of the authors they would like to see and all their works
    if len(matchingNames) == 0:
        print("No results found.\n")
    else:
        selectAuthor = (input("Please select which author you would like to view\n"))
        while selectAuthor.isdigit() == False or int(selectAuthor) <= 0 or int(selectAuthor) > (len(matchingNamesDic)):
            selectAuthor = (input("Invalid selection! Please select a valid option.\n"))

        #Convert userchoice to valid int 
        selectAuthor = int(selectAuthor)
        
        #Prints all the title year and venue of the author
        print("")
        print(f"All work of {matchingNames[selectAuthor - 1]}:")
        query = {"authors" : {"$in": [matchingNames[selectAuthor - 1]]}}
        executeQuery = collection.find(query)
        
        dicList = []
        for dic in executeQuery:
            dicList.append(dic)
        
        dicList = sorted(dicList, key=lambda x: x['year'], reverse = True)

        for dic in dicList:
            print(f"title: {dic['title']}")
            print(f"year: {dic['year']}")
            print(f"venue: {dic['venue']}")
            print("")


    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        print("")
        mainMenu(db)
    elif userChoice == 2:
        exit()

    
def listVenues(db):
    '''
    Prompts user for number
    Displays venue, the number of articles in that venue, and the number of articles that reference a paper in that venue
    '''
    #error checking
    while True:
        try:
            userInput = int(input("Please enter the number of venues you would like to see: "))
            break
        except ValueError:
            print("Please enter a valid number\n") 
    
    
    collection = db['dblp']

    #query to get the number of articles in each venue
   
    test = collection.aggregate([{'$match': {'venue': {'$not': re.compile('^(?![\s\S])')}}}, {'$group':{'_id' : '$venue', 'article_count' : {'$sum' : 1}}}])
    test = list(test)

    print(test)
    #query to get the number of articles that reference a paper in each venue
    venueCountDict =  collection.aggregate([{"$group": {"_id": "$venue", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}])
    for dic in venueCountDict:
        print(dic["_id"] + f"\t| {dic['count']}")
    
    #convert the query results to dictionaries
    #venueCountDict = dict((x, venue) for x, venue in enumerate(venueCount, 1))
    #venueRefCountDict = dict((x, venue) for x, venue in enumerate(venueRefCount, 1))

    
    for x in venueCountDict:
        print(x)
    print(venueCountDict)

    #print the results
    #for key, value in venueCountDict.items():
        #print(f"{key}. | {value['_id']} | {value['count']} | {venueRefCountDict[key]['count']}")

    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        print("")
        mainMenu(db)
    elif userChoice == 2:
        exit()

def addArticle(db):
    '''
    Adds an article to the collection by providing a unique id, a title, a list of authors, and a year
    Error Handling
    '''
    #Connects to dplb collection in the database
    collection = db["dplb"]

    #Prompts the user for a unique id and checks if the id is unique * Reprompts the user for id until id is unique
    unique = False
    while not unique:
        uniqueId = input("Please insert a unique id\n")

        #Checks if id already exists
        a = list(collection.find({"id": uniqueId}))
       
        #Terminate loop if title exists
        if len(a) == 0:
            unique = True
        else:
            #reprompts user for id 
            print("Invalid Input\n")

    #Prompt the user for a title, a list of authors and a year
    title = input("Please insert a title\n")

    allAuthorsListed = False
    authorList = []
    while not allAuthorsListed:
        authorNames = input("Please insert the name of the authors (if you wish to stop adding authors insert `) \n")
        if authorNames == "`":
            allAuthorsListed = True
        else:
            authorList.append(authorNames)

    year = input("Please insert the year of publication\n")
    
    #set abstract and venue to null, references set to an empty array, n_citations set to 0
    venue = ""
    abstract = ""
    references = []
    nCitations = 0
    
    newArticle = [{"abstract": abstract, "authors": authorList, "n_citation": nCitations, "refereces": references, "title": title, "venue":venue, "year": year, "id": uniqueId}]
    collection = db["dplb"]
    collection.insert_many(newArticle)

    print("Successfully added article!")
    
    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        print("")
        mainMenu(db)
    elif userChoice == 2:
        exit()

def exit():
    print("Now exiting, thank you for using our services!")

def main():
    #Prompt user for portNum and insert it into client name
    portNum = inputPortNum()
    client = MongoClient('mongodb://localhost:' + str(portNum))
    db = client["291db"]

    #Calls Main menu function
    mainMenu(db)

    #Close Client when done
    client.close()

if __name__ == "__main__":
    main()
    
