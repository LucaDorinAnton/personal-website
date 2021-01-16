from mongo_session import Mongo
from settings_mngr import BLOG_WRITER_ACC, LOGGING_COL
import datetime as dt

accs = {
    'blog' : BLOG_WRITER_ACC
}

def mongo_log(msg, level, scope):
    m = Mongo()
    doc = {
        'level' : level,
        'timestamp' : dt.datetime.now().timestamp(),
        'message' : msg
    }
    return m.insert_one(accs[scope], LOGGING_COL, doc)

