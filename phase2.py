import pymongo
from pymongo import MongoClient

def inputPortNum():
    '''
    Prompts the user for a Port Num
    Return: Port Num Input (Int)
    '''
    portNum = int(input("Please input a port number. \n"))
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
        searchForArticle(db)
    elif choice == 2:
        #Executes searchForAuthors(db) function
        searchForAuthors(db)
    elif choice == 3:
        #Executes listVenues(db) function
        listVenues(db)
    elif choice == 4:
        #Executes addArticle(db) function
        addArticle(db)
    elif choice == 5:
        #Executes exit function and closes program
        exit()

def searchForArticle(db):
    '''
    Prompts user for keyword
    Displays all Articles matching the keyword
    '''
    #Connects to dplb collection in the database
    collection = db["dplb"]


    #Prompts user for matching keyword or keywords
    userKeywords = input("Please insert a keyword or keywords of the article you would like to search\n")
    keywordsList = userKeywords.split()

    #Search Query
    query = {"n_citation": 0}
    mydoc = collection.find(query)

    print(mydoc.explain()['executionStats'])

    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        mainMenu(db)
    elif userChoice == 2:
        exit()

def searchForAuthors(db):
    '''
    User should be able to provide one or more keywords and see all authors whose names contain the keywords
    the matches should be case insensitive
    For each matching article, display the id, the title, the year, and the venue fields.
    the user should be able to select an article to see all fields including the abstract and the authors in addition to the fields listed above.
    if the article is referenced by other articles, the id, the title, and the year of those references should be also listed.

    '''
    
    #Creates Collection
    collection = db["dplb"]

    #Prompts user for a keyword
    keyword = input("Please enter a keyword to search for authors: ")
    keyword = f"\"{keyword}\" "
    
    #query to find items in collection with common author names
    query = [
            {"$match" : {"$text": {"$search": keyword}}},
            {"$lookup" :
                {
                    "from" : "dplb",
                    "localField" : "authors", 
                    "foreignField" : "authors",
                    "as" : "titlebas_rat"
                }
            },
            {"$match" : {"titlebas_rat.numVotes" : {"$gte" : keyword}}},
            {"$sort" : {"titlebas_rat.averageRating" : -1}},
            {"$project" : {"primaryTitle" : 1, "titlebas_rat.numVotes" : 1, "titlebas_rat.averageRating" : 1}}
    ]

    query = collection.find({"authors": { "$elemMatch": { "$regex": "/.*"+keyword+".*/" }}})
    
    authorList = []
    for author in query:
        authorList.append({"names": author["authors"]})
    
    print(authorList)

    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
        mainMenu(db)
    elif userChoice == 2:
        exit()

def listVenues(db):
    '''
    Prompts user for number
    Displays venue, the number of articles in that venue, and the number of articles that reference a paper in that venue
    '''
    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
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

    year = int(input("Please insert the year of publication\n"))
    
    #set abstract and venue to null, references set to an empty array, n_citations set to 0
    venue = None
    abstract = None
    references = []
    nCitations = 0
    
    newArticle = [{"abstract": abstract, "authors": authorList, "n_citation": nCitations, "refereces": references, "title": title, "venue":venue, "year": year, "id": uniqueId}]
    collection = db["dplb"]
    collection.insert_many(newArticle)

    print("Successfully added article!")

    #Reprompt user for user choice
    userChoice = int(input("Would you like to go back to the main menu or exit? \n1.Go back to main menu \n2.Exit\n"))
    if userChoice == 1:
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

if __name__ == "__main__":
    main()
    