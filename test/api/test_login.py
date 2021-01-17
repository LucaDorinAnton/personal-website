import requests as r
import hashlib
import datetime as dt
import json

ip = '172.19.0.1'
inp = input("Pwd? > ")
ha = hashlib.sha256()
ha.update(inp.encode('utf-8'))
h = ha.hexdigest()

base = 'http://localhost:5000'

s = r.Session()

def generate_sha(p_sha, salt, date, ip):
    h = hashlib.sha256()
    inp = p_sha + salt + date + ip
    h.update(inp.encode('utf-8'))
    return h.hexdigest()

print(s.get(base + '/heartbeat').status_code)

r_check = s.get(base + '/blogLoginInfo')

salt = json.loads(r_check.text)['salt']

now = str(dt.datetime.now().date())

sha  = generate_sha(h, salt, now, ip)

s.get(base + '/blogLoginInfo')

r_login = s.post(base + '/blogLogin', json={
    'sha256' : sha,
    'salt' : salt
})
print(salt, now, ip)
print(r_login.text)
print('Cookies: {}'.format(r_login.cookies['UID']))

new_cookies = {
    'UID' : r_login.cookies['UID']
}

test_login = s.get(base + '/heartbeat', cookies=new_cookies)
print(test_login.status_code, test_login.text)

