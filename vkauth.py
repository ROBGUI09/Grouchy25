import requests
import hashlib
import urllib
import random
import string
import re
import json


class VkAndroidApi(object):
    session = requests.Session()
    session.headers = {
      "User-Agent": "VKAndroidApp/4.13.1-1206 (Android 4.4.3; SDK 19; armeabi; ; ru)",
      "Accept": "image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*"
    }


    def _get_auth_params(self, login, password):
        return {
            'grant_type': 'password',
            'scope': 'nohttps,audio',
            'client_id': 2274003,
            'client_secret': 'hHbZxrka2uZ6jB1inYsH',
            'validate_token': 'true',
            'username': login,
            'password': password
        }


    def __init__(self, login = None, password = None, token = None, secret = None, v=5.95):
        self.v = v
        self.device_id = "".join( random.choice(string.ascii_lowercase + string.digits) for i in range(16))
        if token is not None and secret is not None:
            self.token = token
            self.secret = secret
        else:
            a = self.session.get("https://oauth.vk.com/token", params=self._get_auth_params(login, password))
            print(a.text)
            answer = a.json()
            if ("error" in answer): raise PermissionError(json.dumps(answer, indent=2))
            self.secret = answer["secret"]
            self.token = answer["access_token"]
            self.method('execute.getUserInfo', func_v=9)
            self.method('auth.refreshToken', lang='ru')


    def method(self, method, **params):
        url = ("/method/{method}?v={v}&access_token={token}&device_id={device_id}"
        .format(method=method,v=self.v,token=self.token,device_id=self.device_id)
            +"".join("&%s=%s"%(i,params[i]) for i in params if params[i] is not None)
        )
        return self._send(url, params, method)


    def _send(self, url, params = None, method = None, headers = None):
        hash = hashlib.md5((url + self.secret).encode()).hexdigest()
        if method is not None and params is not None:
            url = ("/method/{method}?v={v}&access_token={token}&device_id={device_id}".format(method=method,token=self.token,device_id=self.device_id,v=self.v)
                + "".join(
                "&"+i+"="+urllib.parse.quote_plus(str(params[i])) for i in params if(params[i] is not None)
                ))
        if headers is None:
            return self.session.get('https://api.vk.com'+url+"&sig="+hash).json()
        else:
            return self.session.get('https://api.vk.com'+url+"&sig="+hash, headers=headers).json()

    _pattern = re.compile(r'/[a-zA-Z\d]{6,}(/.*?[a-zA-Z\d]+?)/index.m3u8()')


    def to_mp3(self,url):
        return self._pattern.sub(r'\1\2.mp3',url)
