import requests
import json
import datetime


class AutoReport(object):

    def __init__(self, username, password, owner) -> None:
        self.url = 'https://shxxybqq.shec.edu.cn'
        self.host = 'shxxybqq.shec.edu.cn'
        self.username = username
        self.password = password
        self.owner = owner
        self.usercode = ''
        self.public_headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.23(0x1800172e) NetType/WIFI Language/zh_CN',
            'Accept-Encoding': 'gzip, deflate, compress, br',
            'content-type': 'application/json',
            'connection': 'keep-alive',
            'Referer': 'https://servicewechat.com/wxe65bc0702880fff0/12/page-frame.html'
        }

    
    def public_request(self, path, data=None, headers=None):
        try_again = 0
        while try_again < 5:
            try_again += 1
            if data is None:
                data = {
                    "Usercode": self.usercode
                }
            if headers is None:
                headers = self.public_headers
            try:
                if headers['content-type'] == 'application/json':
                    _response = requests.post(self.url + path, headers=headers, json=data)
                else: _response = requests.post(self.url + path, headers=headers, data=data)
            except Exception as e:
                continue
            else:
                if _response.status_code != 200: continue
                try:
                    _response = json.loads(_response.text)
                except:
                    continue
                else:
                    return _response
        print(_response.text)
        return False
    

    def login(self):
        _path = '/LoginMng/login'
        _data = {
            "Usercode": self.username,
            "Password": self.password,
            "Type": 0
        }
        _response = self.public_request(path=_path, data=_data)
        if not _response: return False
        else:
            if _response['RetValue'] and _response['RetStatus'] == 100:
                self.usercode = _response['RetValue']
                return True
            else: return False

    
    def get_user(self):
        _path = '/HomePage/GetUserByRole'
        _data = {
            "Usercode": self.usercode
        }
        return self.public_request(path=_path, data=_data)
    

    '''
        无人缺勤填报
    '''
    def no_absense_check(self):
        _report_types = ['无人缺勤', '无人缺课']
        _path = '/NoAbsenceMngApi/index'
        _data = {
            "p": 1,
            "Usercode": self.usercode,
            "startdate": str(datetime.date.today()) + " 至 " + str(datetime.date.today()),
            "wurenleixing": "",
            "ps": 10
        }
        _response = self.public_request(path=_path, data=_data)
        if not _response: return _report_types
        try:
            _report_data = _response['data']
            for _report_history in _report_data:
                try: _t = _report_history['wurenleixing']
                except: pass
                else:
                    if _t in _report_types: _report_types.remove(_t)
            if len(_report_types) == 0: return False
            else: return  _report_types
        except: return _report_types
    

    def no_absense_report(self, report_type):
        _path = '/NoAbsenceMngApi/Execute'
        _headers = self.public_headers
        _headers['content-type'] = 'application/x-www-form-urlencoded'
        now = datetime.datetime.now()
        year = str(int(now.strftime('%Y')))
        month = str(int(now.strftime('%m')))
        day = str(int(now.strftime('%d')))
        _data = {
            "Usercode": self.usercode,
            "Docmd": "add",
            "WuRenLeiXing": report_type,
            "TianBaoDate": year+'-'+month+'-'+day, 
            'TianBaoRen': self.owner
        }
        _response = self.public_request(path=_path, data=_data, headers=_headers)
        if not _response: return False, -1
        if not (_response['RetValue'] and _response['RetStatus'] == 100): return False, _response
        return True, _response




if __name__ == '__main__':
    test = AutoReport('', '', '')
    if not test.login():
        print('登录失败 请检查')
        exit()
    userinfo = test.get_user()
    if not userinfo:
        print('获取用户信息失败')
        exit()
    print("已登录 {} ".format(userinfo['CommunityName']))
    report_types = test.no_absense_check()
    if report_types:
        for report_type in report_types:
            if report_type == "无人缺勤": test.no_absense_report(1)
            elif report_type == "无人缺课": test.no_absense_report(0)
    else:
        print('填报完成')
        exit()


