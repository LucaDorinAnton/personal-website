from pymongo import MongoClient
from settings_mngr import SECRETS_READER_ACC, SECRETS_READER_PWD
from settings_mngr import SECRETS_WRITER_ACC, SECRETS_WRITER_PWD
from settings_mngr import BLOG_READER_ACC, BLOG_READER_PWD
from settings_mngr import BLOG_WRITER_ACC, BLOG_WRITER_PWD
from settings_mngr import SECRETS_DB, BLOG_DB, MONGO_HOST


mongo_urls = {
    SECRETS_READER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(SECRETS_READER_ACC,SECRETS_READER_PWD, MONGO_HOST, SECRETS_DB),
        SECRETS_DB],
    SECRETS_WRITER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(SECRETS_WRITER_ACC, SECRETS_WRITER_PWD, MONGO_HOST, SECRETS_DB),
        SECRETS_DB
    ],
    BLOG_READER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(BLOG_READER_ACC, BLOG_READER_PWD, MONGO_HOST, BLOG_DB),
        BLOG_DB],
    BLOG_WRITER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(BLOG_WRITER_ACC, BLOG_WRITER_PWD, MONGO_HOST, BLOG_DB),
        BLOG_DB]
}


class Mongo:
    '''
    Manages and mediates call to the MongoDB database.
    A new instance of Mongo should be created for each database call.
    Each instance should be responsible for creating and then destroying
    the MongoClient instance needed for each database acces request.
    As such, only the methods which fullfil this promise should be use,
    the rest should be considered private.
    '''

    client = None
    

    def createClient(self, account):
        '''
        Private method. Creates a new MongoClient if one doesn't already exist.
        Needs an account for the client to login as.
        '''

        if self.client is None: 
            self.client =  MongoClient(mongo_urls[account][0])


    def killClient(self):
        '''
        Private method. Kills a MongoClient if it exists.
        '''
        
        if self.client != None:
            self.client.close()
            self.client = None


    def getClient(self, account):
        '''
        Private method. Creates a new client and returns it. Needs an account 
        '''
        
        self.createClient(account)
        return self.client


    def getDB(self, account, db = 'DEFAULT'):
        '''
        Private method. returns a database object retrieved as a certain account.
        '''
        
        self.createClient(account)
        if db == 'DEFAULT':
            return self.client[mongo_urls[account][1]]
        else:
            return self.client[db]


    def getCol(self, account, col, db='DEFAULT'):
        '''
        Private method. Returns a column from a database as a certain account.
        '''
        
        self.createClient(account)
        if db == 'DEFAULT':
            db = self.getDB(account)
        else:
            db == self.getDB(account, db)
        return db[col]


    def getByQuery(self, account, col, query, db='DEFAULT'):
        '''
        Public method. Returns the result of running a query 
        on a column of a database as a certain account. 
        '''
        
        c = self.getCol(account, col, db)
        res = c.find(query)
        self.killClient()
        return res


    def getOneByQuery(self, account, col, query, db='DEFAULT'):
        '''
        Public method. Returns the first element retrieved after running
        a query on a column of a database as a certain account.
        Raises an IndexError if the query returns empty.
        '''
        return self.getByQuery(account, col, query, db)[0]


    def getAll(self, account, col, db='DEFAULT'):
        '''
        Public method. Returns all object from a collection 
        from a database as a certain account. 
        '''
        
        return self.getByQuery(account, col, {}, db)


    def getFirst(self, account, col, db='DEFAULT'):
        '''
        Public method. Returns the first object to be returned
        from a collection from a database as a certain account.
        '''

        return self.getOneByQuery(account, col, {}, db)

    def getLast(self, account, col, db='DEFAULT'):
        '''
        Public method. Returns the last object created
        from a collection from a database as a certain account.
        '''

        c = self.getCol(account, col, db)
        res = c.find().skip(c.count() - 1)[0]
        self.killClient()
        return res

    def updateOne(self, account, col, query, update, db='DEFAULT'):
        '''
        Public Method. Updates one document matching the query on a collection
        from a database as an account and returns the updated document,
        assuming it is still identifiable by the same query.
        '''

        c = self.getCol(account, col, db)
        c.update_one(query, {'$set': update})
        res = self.getByQuery(account, col, query, db)
        self.killClient()
        return res


    def updateFirst(self, account, col, update, db='DEFAULT'):
        '''
        Public Method. Retrieves the first object from a collection from a database as
        an account and applies an update to it, then saves it in the collection.
        Returns the updated object, assuming it is identifiable by the same collection.
        '''

        obj = self.getFirst(account, col, db)
        query = obj_to_id(obj)
        return self.updateOne(account, col, query, update, db)[0]


    def updateByQuery(self, account, col, query, update, db='DEFAULT'):
        '''
        Public Method. Retrieves objects from a collection from a database 
        as an account using a query and then applies the update to all objects
        and saves them in the database. Returns the updated objects, 
        assuming they are still identifiable by the same query.
        '''
        
        c = self.getCol(account, col, db)
        c.update_many(query, {'$set': update})
        res = self.getByQuery(account, col, query, db)
        self.killClient()
        return res

    def updateAll(self, account, col, update, db='DEFAULT'):
        '''
        Public method. Retrieves all objects from a from a collection,
        from a database, as an account, applies an update to them,
        and then returns them.
        '''

        c = self.getCol(account, col, db)
        c.update_many({}, {'$set': update})
        res = self.getAll(account, col, db)
        self.killClient()
        return res        


    def insertOne(self, account, col, doc, db='DEFAULT'):
        '''
        Public method. Insert one document into a collection
        from a database as an account. The document may
        or may not contain an _id field.
        Returns True.
        '''
        c = self.getCol(account, col, db)
        c.insert_one(doc)
        self.killClient()
        return True


    def inserMany(self, account, col, docs, db='DEFAULT'):
        '''
        Public method. Inserts a list of documents into a collection
        from a database as an account. The documents may or may not
        contain an _id field.
        Returns True
        '''
        c = self.getCol(account, col, db)
        c.insert_many(docs)
        self.killClient()
        return True


    def deleteAll(self, account, col, db='DEFAULT'):
        '''
        Public method. Deletes all documents from a collection
        from a database as an account. Returns True.
        '''
        c = self.getCol(account, col, db)
        c.delte_many({})
        self.killClient()
        return True


    def deleteFirst(self, account, col, db='DEFAULT'):
        '''
        Public method. Selects the first document from a collection
        from a a database as an account and deletes it. Returns True
        '''

        doc = self.getFirst(account, col, db)
        c =  self.getCol(account, col, db)
        c.delete_one(obj_to_id(doc))
        self.killClient()
        return True


    def deleteOneByQuery(self, account, col, query, db='DEFAULT'):
        '''
        Public method. Deletes a document from a collection from
        a database as an account based on a query. Returns True.
        '''

        c = self.getCol(account, col, db)
        c.delete_one(query)
        self.killClient()
        return True

    
    def deleteManyByQuery(self, account, col, query, db='DEFAULT'):
        '''
        Public method. Deletes all document from a collection from
        a database as an account which are selected by a query. 
        Returns True.
        '''

        c = self.getCol(account, col, db)
        c.delete_many(query)
        self.killClient()
        return True


def obj_to_id(obj):
    return  {
                '_id' : obj['_id']
            }