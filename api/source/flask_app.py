import hmac
import hashlib
import datetime as dt
import random
from flask import Flask, request, jsonify, abort, make_response
from functools import wraps

from settings_mngr import SECRETS_READER_ACC, SECRETS_WRITER_ACC
from mongo_session import Mongo
from log_mngr import mongo_log

app = Flask(__name__)

LOGIN_REQUEST_TIMEOUT = 3

WARNING_NO_COOKIE = 'Resource access denied - No UID cookie detected'
WARNING_SID_MISMATCH = 'Resource access denied- SID mismatch '
WARNING_SIG_MISMATCH = 'Resource access denied - Signature could not be verified'

WARNING_REQUEST_TIMEOUT = 'Login attempt failed - Login request came after information time-out'
WARNING_SHA_MISMATCH = 'Login attempt failed - Client provided incorrect SHA'

INFO_LOGIN_SUCCESS = 'Client logged in successfully'

def loggged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'UID' not in request.cookies.keys():
            app.logger.warning(WARNING_NO_COOKIE)
            mongo_log(WARNING_NO_COOKIE, 'WARNING', 'blog')
            abort(400)
        cl = Mongo()
        s_sesh = cl.getByQuery(SECRETS_READER_ACC, 'sessions', {'scope' : 'blog'})[0]
        r_sid, r_sig = request.cookies.get('UID').split('-')
        s_sid = s_sesh['sid']
        s_sig = s_sesh['sig']
        if r_sid != s_sid:
            app.logger.warning(WARNING_SID_MISMATCH)
            mongo_log(WARNING_SID_MISMATCH, 'WARNING', 'blog')
            abort(400)
        if r_sig != s_sig:
            app.logger.warning(WARNING_SIG_MISMATCH)
            mongo_log(WARNING_SIG_MISMATCH, 'WARNING', 'blog')
            abort(400)
        return f(*args, **kwargs)
    return decorated_function




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

    if td > dt.timedelta(seconds=LOGIN_REQUEST_TIMEOUT):
        app.logger.warning(WARNING_REQUEST_TIMEOUT)
        mongo_log(WARNING_REQUEST_TIMEOUT, 'WARNING', 'blog')
        abort(400)

    res_date = str(res_dt.date())
    s_sha = generate_sha(res['sha256'], res['salt'], res_date, res['ip'])
    body = request.get_json()
    r_sha = body['sha256']

    if r_sha != s_sha:
        app.logger.warning(WARNING_SHA_MISMATCH)
        mongo_log(WARNING_SHA_MISMATCH, 'WARNING', 'blog')
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
    response = make_response('Logged In\nsid: {}\nsig: {}'.format(sid, sig))
    c_id='UID'
    c_val = '{}-{}'.format(sid, sig)
    response.set_cookie(c_id, value=c_val, expires=expire_at, path='/', secure=True, httponly=True)
    app.logger.info(INFO_LOGIN_SUCCESS)
    mongo_log(INFO_LOGIN_SUCCESS, 'WARNING', 'blog')
    return response, 200


@app.route('/heartbeat', methods=['GET'])
@loggged_in
def heartbeat():
    return jsonify({'status' : 'ok'}), 200



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
    NUMS = '0123456789'
    if nums_only:
        ALPHABET = NUMS
    else:
        ALPHABET = NUMS + 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for i in range(len):
        chars.append(random.choice(ALPHABET))
    return ''.join(chars)