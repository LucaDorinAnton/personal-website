import requests as r
import hashlib
import datetime as dt
import json
import unittest

def generate_sha(p_sha, salt, date, ip):
    '''
    Take a sha256 of a concatenation of four strings. 
    The strings should be:
        - p_sha - the sha256 of the password
        - salt - a random string of 16 alfanumeric characters
        - date - the UNIX timestamp of the date of the request
        - ip - the public IP of the client
        '''
    
    h = hashlib.sha256()
    inp = p_sha + salt + date + ip
    h.update(inp.encode('utf-8'))
    return h.hexdigest()

class TestLogin(unittest.TestCase):

    ip = '172.18.0.1'
    base = 'http://localhost:5000'
    s = r.Session()

    @classmethod
    def setUpClass(cls):
        inp = input("Pwd? > ")
        ha = hashlib.sha256()
        ha.update(inp.encode('utf-8'))
        cls.h = ha.hexdigest()

    def testHeartBeatNoLogin(self):
        code = self.s.get(self.base + '/heartbeat').status_code
        self.assertEqual(code, 400, 'Expected code 400. Got code {}'.format(code))

    def testBlogLoginInfo(self):
        r_check = self.s.get(self.base + '/blogLoginInfo')
        json_dict = json.loads(r_check.text)
        self.assertIn('salt', json_dict.keys(), 'Call to /blogLoginInfo contained no "salt" field. Got: {} '.format(r_check.text))

    def testBlogLoginPositive(self):
        r_check = self.s.get(self.base + '/blogLoginInfo')
        json_dict = json.loads(r_check.text)
        salt = json_dict['salt']
        now = str(dt.datetime.now().date())
        sha  = generate_sha(self.h, salt, now, self.ip)
        r_login = self.s.post(self.base + '/blogLogin', json={
            'sha256' : sha,
            'salt' : salt
        })
        cookies = r_login.cookies.get_dict()
        self.assertIn('UID', cookies.keys(), 'Legitimate call to /blogLogin did not return a UID cookie')

    def testBlogLoginNegative(self):
        r_login = self.s.post(self.base + '/blogLogin', json={
            'sha256' : 'somesha',
            'salt' : 'somesalt'
        })
        self.assertEqual(400, r_login.status_code, 'Ilegimate call to /blogLogin should return a 400. It returned {}'.format(r_login.status_code))
        self.assertNotIn('UID', r_login.cookies.get_dict().keys(), 'Ilegitimate call to /blogLogin should not return a UID cookie. It returned {}'.format(str(r_login.cookies.keys())))

    def testBlogLoginDoS(self):
        r_check = self.s.get(self.base + '/blogLoginInfo')
        json_dict = json.loads(r_check.text)
        salt = json_dict['salt']
        now = str(dt.datetime.now().date())
        sha  = generate_sha(self.h, salt, now, self.ip)
        for i in range(3):
            self.s.get(self.base + '/blogLoginInfo')
        r_login = self.s.post(self.base + '/blogLogin', json={
            'sha256' : sha,
            'salt' : salt
        })
        cookies = r_login.cookies
        self.assertIn('UID', cookies.get_dict().keys(), 'Legitimate call to /blogLogin did not return a UID cookie under basic DoS attack.')   


    def testHeartBeatLoggedIn(self):
        r_check = self.s.get(self.base + '/blogLoginInfo')
        json_dict = json.loads(r_check.text)
        salt = json_dict['salt']
        now = str(dt.datetime.now().date())
        sha  = generate_sha(self.h, salt, now, self.ip)
        r_login = self.s.post(self.base + '/blogLogin', json={
            'sha256' : sha,
            'salt' : salt
        })
        cookies = r_login.cookies
        self.assertIn('UID', cookies.get_dict().keys(), 'No UID cookie found when accessing /heartbeat.')
        new_cookies = {
            'UID' : cookies['UID']
        }
        test_heartbeat = self.s.get(self.base + '/heartbeat', cookies=new_cookies)
        self.assertEqual(200, test_heartbeat.status_code, 'Logged in Request to /heartbeat should return a 200. It returned a {}.'.format(test_heartbeat.status_code))
        json_dict = json.loads(test_heartbeat.text)
        self.assertIn('status', json_dict.keys(), 'Logged in Request to /heartbeat should return a JSON obj containing the "status" field. {}'.format(json_dict.keys()))
        self.assertEqual('ok', json_dict['status'], 'Logged in Request to /heartbeat should return a JSON obj containing the "status" field with the "ok" value. {}'.format(json.dumps(json_dict)))



if __name__ == '__main__':
    unittest.main()
