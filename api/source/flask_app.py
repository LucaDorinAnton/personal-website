import hashlib
import datetime as dt
import random

from flask import Flask, request, jsonify, abort

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
    cl.updateFirst(SECRETS_WRITER_ACC, 'blog', {
        'salt' : salt,
        'timestamp' : str(ts),
        'ip' : request.remote_addr
    })

    res = {'salt' : salt}
    return jsonify(res), 200




@app.route('/blogLogin', methods=['POST'])
def blogLogin():
    req_dt = dt.datetime.now()
    body = request.get_json()
    r_sha = body['sha256']
    cl = Mongo()
    res = cl.getFirst(SECRETS_READER_ACC, 'blog')
    res_dt = dt.datetime.fromtimestamp(float(res['timestamp']))
    td = req_dt - res_dt

    if td > dt.timedelta(seconds=3):
        print("ERROR --- REQUEST CAME AFTER MORE THAN 3 SECONDS")
        abort(400)

    res_date = str(res_dt.date())
    s_sha = generate_sha(res['sha256'], res['salt'], res_date, res['ip'])

    if r_sha != s_sha:
        print("ERROR --- REQUEST PROVIDED WRONG SHA")
        abort(400)
    
    return "Logged In", 200




def generate_sha(p_sha, salt, date, ip):
    h = hashlib.sha256()
    inp = p_sha + salt + date + ip
    h.update(inp.encode('utf-8'))
    return h.hexdigest()

def generate_salt():
    chars = []
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    return "".join(chars)