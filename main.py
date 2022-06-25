import requests
import json
import datetime


def isHoliday(datestr=None):
    if datestr is None:
        datestr = str(datetime.date.today())
    week = datetime.datetime.strptime(datestr, '%Y-%m-%d').weekday()
    now = datetime.datetime.now()
    year = str(int(now.strftime('%Y')))
    try:
        holidays_data = requests.get('https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{}.json'.format(year)).json()
    except Exception as e: return False
    for holiday in holidays_data['days']:
        if holiday['date'] == datestr and holiday['isOffDay']: return True
        elif holiday['date'] == datestr and not holiday['isOffDay']: return False
    if week == 5 or week == 6: return True
    return False


def get_non_zero_date():
    now = datetime.datetime.now()
    year = str(int(now.strftime('%Y')))
    month = str(int(now.strftime('%m')))
    day = str(int(now.strftime('%d')))
    return year, month, day


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
    

    def public_check(self, response):
        if not response: return False
        if not response['RetValue']: return False
        if not response['RetStatus'] == 100: return False
        return True
    

    def login(self):
        _path = '/LoginMng/login'
        _data = {
            "Usercode": self.username,
            "Password": self.password,
            "Type": 0
        }
        return self.public_request(path=_path, data=_data)

    
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
        year, month, day = get_non_zero_date()
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


    '''
        节假日停课上报
    '''
    def suspension_report(self, reason='周末/节假日停课', type='全校'):
        _path = '/SuspensionMngApi/Execute?Docmd'
        _headers = self.public_headers
        _headers['content-type'] = 'application/x-www-form-urlencoded'
        year, month, day = get_non_zero_date()
        _data = {
            "SuspnStartDate": year+'-'+month+'-'+day,
            "SuspnEndDate": year+'-'+month+'-'+day,
            "SuspensionReason": reason,
            "SuspensionType": type,
            "SuspensionGrade": "",
            "SuspensionClass": "",
            "DiseaseName": "",
            "Usercode": self.usercode,
            "Docmd": "add"
        }
        return self.public_request(path=_path, data=_data, headers=_headers)



if __name__ == "__main__":
    username = ''
    password = ''
    owner = ''
    report = AutoReport(username, password, owner)
    doLogin = report.login()
    if not report.public_check(doLogin): raise Exception ('登录失败')
    report.usercode = doLogin['RetValue']
    if isHoliday():
        print("节假日上报")
        resp = report.suspension_report()
        if report.public_check(resp): 
            print("上报成功")
            exit()
        else:
            print("上报失败", resp['RetValue'], "StatusCode:", resp['RetStatus'])
            exit()
    else:
        print("工作日上报")
        # ...
        