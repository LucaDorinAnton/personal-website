from pymongo import MongoClient
from settings_mngr import SECRETS_READER_ACC, SECRETS_READER_PWD, SECRETS_WRITER_ACC, SECRETS_WRITER_PWD, SECRETS_DB, MONGO_HOST
######################

mongo_urls = {
    SECRETS_READER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(SECRETS_READER_ACC,SECRETS_READER_PWD, MONGO_HOST, SECRETS_DB),
        SECRETS_DB],
    SECRETS_WRITER_ACC : [
        'mongodb://{}:{}@{}/{}'.format(SECRETS_WRITER_ACC, SECRETS_WRITER_PWD, MONGO_HOST, SECRETS_DB),
        SECRETS_DB
    ]
}

######################

class Mongo:

    client = None
    
    def createClient(self, account):
        if self.client is None: 
            self.client =  MongoClient(mongo_urls[account][0])

    def killClient(self):
        if self.client != None:
            self.client.close()
            self.client = None

    def getClient(self, account):
        self.createClient(account)
        return self.client

    def getDB(self, account, db = 'DEFAULT'):
        self.createClient(account)
        if db == 'DEFAULT':
            return self.client[mongo_urls[account][1]]
        else:
            return self.client[db]


    def getCol(self, account, col, db='DEFAULT'):
        self.createClient(account)
        if db == 'DEFAULT':
            db = self.getDB(account)
        else:
            db == self.getDB(account, db)
        return db[col]

    def getByQuery(self, account, col, query, db='DEFAULT'):
        c = self.getCol(account, col, db)
        res = c.find(query)
        self.killClient()
        return res

    def getAll(self, account, col, db='DEFAULT'):
        return self.getByQuery(account, col, {}, db)

    def getFirst(self, account, col, db='DEFAULT'):
        return self.getAll(account, col, db)[0]


    def updateFirst(self, account, col, update, db='DEFAULT'):
        obj = self.getFirst(account, col, db)
        query = obj_to_id(obj)
        return self.updatebyQuery(account, col, query, update, db)[0]

    def updatebyQuery(self, account, col, query, update, db='DEFAULT'):
        c = self.getCol(account, col, db)
        c.update_one(query, {'$set': update})
        res = self.getByQuery(account, col, query, db)
        self.killClient()
        return res


def obj_to_id(obj):
    return  {
                '_id' : obj['_id']
            }