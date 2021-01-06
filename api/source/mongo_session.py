from pymongo import MongoClient

######################
# HARDCODING (for now)
mongo_urls = {
    'secrets_reader' : [
        'mongodb://secretsReader:somesecret4@personal-website_mongo_1/secrets',
        'secrets'],
    'secrets_writer' : [
        'mongodb://secretsWriter:somesecret5@personal-website_mongo_1/secrets',
        'secrets'
    ]
}

######################

class Mongo:

    client = None
    
    def createClient(self, account):
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

    def getAll(self, account, col, db='DEFAULT'):
        c = self.getCol(account, col, db)
        res = []
        for i in c.find({}):
            res.append(i)
        self.killClient()
        return res

    def getFirst(self, account, col, db='DEFAULT'):
        c = self.getCol(account, col, db)
        res = c.find({})[0]
        self.killClient()
        return res

    def updateFirst(self, account, col, update, db='DEFAULT'):
        c = self.getCol(account, col, db)
        res = self.getFirst(account, col, db)
        keys = update.keys()
        for key in keys:
            res[key] = update[key]
        c.update({}, res)
        res = self.getFirst(account, col, db)
        self.killClient()
        return res
