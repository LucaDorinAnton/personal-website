import requests as r
import hashlib
import datetime as dt
import json

ip = '172.18.0.1'
inp = input("Pwd? > ")
ha = hashlib.sha256()
ha.update(inp.encode('utf-8'))
h = ha.hexdigest()

base = 'http://localhost:5000'

def generate_sha(p_sha, salt, date, ip):
    h = hashlib.sha256()
    inp = p_sha + salt + date + ip
    h.update(inp.encode('utf-8'))
    return h.hexdigest()

r_check = r.get(base + '/blogLoginInfo')

salt = json.loads(r_check.text)['salt']

now = str(dt.datetime.now().date())

sha  = generate_sha(h, salt, now, ip)

r_login = r.post(base + '/blogLogin', json={
    'sha256' : sha
})
print(salt, now, ip)
print(r_login.text)
print('Cookies: {}'.format(r_login.cookies['UID']))