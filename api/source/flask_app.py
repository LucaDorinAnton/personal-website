import hmac
import hashlib
import datetime as dt
import random

from flask import Flask, request, jsonify, abort, make_response

from mongo_session import Mongo


app = Flask(__name__)

######################
# HARDCODING (for now)
SECRETS_READER_ACC = "secrets_reader"
SECRETS_WRITER_ACC = "secrets_writer"
######################

# Return info necessary to build sha256 digest of writer password
# Specifically, return a random 16 character salt
# A request to this  resource will also update the db with
# the new salt, as well as the current date, the ip of the requester
# and the time of the request. This information will be later used to
# when the requester subsequently tries to log in. 
@app.route('/blogLoginInfo', methods=['GET'])
def blogLoginInfo():
    cl = Mongo()
    salt = generate_salt()
    now = dt.datetime.now()
    ts = now.timestamp()
    cl.updateFirst(SECRETS_WRITER_ACC, 'blog_writer', {
        'salt' : salt,
        'timestamp' : str(ts),
        'ip' : request.remote_addr
    })

    res = {'salt' : salt}
    return jsonify(res), 200




@app.route('/blogLogin', methods=['POST'])
def blogLogin():
    req_dt = dt.datetime.now()
    cl = Mongo()
    res = cl.getFirst(SECRETS_READER_ACC, 'blog_writer')
    res_dt = dt.datetime.fromtimestamp(float(res['timestamp']))
    td = req_dt - res_dt

    if td > dt.timedelta(seconds=3):
        app.logger.info("ERROR --- REQUEST CAME AFTER MORE THAN 3 SECONDS")
        abort(400)

    res_date = str(res_dt.date())
    s_sha = generate_sha(res['sha256'], res['salt'], res_date, res['ip'])
    body = request.get_json()
    r_sha = body['sha256']

    if r_sha != s_sha:
        app.logger.info("ERROR --- REQUEST PROVIDED WRONG SHA")
        to_log = r_sha + " - " + s_sha + " - " + str(res)
        app.logger.info(to_log)
        abort(400)
    
    sid, sig = generate_sid()
    cl = Mongo()
    set_at = dt.datetime.now().timestamp()
    expire_at = (dt.datetime.now() + dt.timedelta(days=7)).timestamp()
    cl.updatebyQuery(SECRETS_WRITER_ACC, 'sessions', {'scope' : 'blog'}, {
        'sid' : sid,
        'sig' : sig,
        'set_at': set_at,
        'expire_at': expire_at
    })
    response = make_response("Logged In\nsid: {}\nsig: {}".format(sid, sig))
    c_id="UID"
    c_val = "{}-{}".format(sid, sig)
    response.set_cookie(c_id, value=c_val, expires=expire_at, path='/', secure=True, httponly=True)

    return response, 200


def generate_sid():
    sid = generate_salt(nums_only=True)
    cl = Mongo()
    key = cl.getByQuery(SECRETS_WRITER_ACC, 'keys', {'scope' : 'blog'})[0]['key']
    sig = hmac.new(key.encode('utf-8'), 
        msg=sid.encode('utf-8'),
        digestmod=hashlib.sha256).hexdigest()
    return sid, sig
    



def generate_sha(p_sha, salt, date, ip):
    h = hashlib.sha256()
    inp = p_sha + salt + date + ip
    h.update(inp.encode('utf-8'))
    return h.hexdigest()


def generate_salt(nums_only=False, len=16):
    chars = []
    NUMS = "0123456789"
    if nums_only:
        ALPHABET = NUMS
    else:
        ALPHABET = NUMS + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for i in range(len):
        chars.append(random.choice(ALPHABET))
    return "".join(chars)