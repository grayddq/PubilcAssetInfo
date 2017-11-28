# -*- coding: utf-8 -*-
import json, urllib2
NAME, VERSION, AUTHOR, LICENSE = "Assets Info", "V0.1", "咚咚呛", "Public (FREE)"  # 版本信息

# 获取DNSPOD的域名列表
# 只要A记录和CNAME 如需要其他的请修改代码['A','CANME']
class DNSPod_domain:
    def __init__(self, login_token, filter_domain, Debug=True):
        self.domain_list, self.login_token, self.temp_domain_list, self.regex_domain_list = [], login_token, [], []
        self.filter_domain = '' if not filter_domain else filter_domain
        self.Debug = Debug
        self.get_domain()

    def get_reslut(self, type, domain_id=None):
        try:
            body_data = 'login_token=' + self.login_token + '&format=json'
            if domain_id: body_data += "&domain_id=" + str(domain_id)
            url = "https://dnsapi.cn/Domain.List" if type == "domain" else "https://dnsapi.cn/Record.List"
            request = urllib2.Request(url, body_data)
            json_response = json.loads(urllib2.urlopen(request).read())
        except:
            json_response = None
        return json_response

    def get_domain(self):
        response = self.get_reslut('domain')
        if response == None: return
        if response['status']['code'] == '1':
            for data in response['domains']:
                if data['status'] == 'enable':
                    sub_response = self.get_reslut('sub_domain', data['id'])
                    if sub_response == None: continue
                    if sub_response['status']['code'] == '1':
                        for records_data in sub_response['records']:
                            if records_data['type'] in ['A', 'CNAME'] and records_data['name'] != '@':
                                if records_data['name'].replace('.', '').isalnum():
                                    self.temp_domain_list.append(records_data['name'] + "." + data['name'])
                                else:
                                    self.regex_domain_list.append(records_data['name'] + "." + data['name'])

        self.domain_list = self.temp_domain_list + self.regex_domain_list

        if self.Debug: print u"\nDNSPOD域名如下：" if len(self.temp_domain_list) > 0 else u'DNSPod常规DNS解析域名：未发现'
        for domain in list(set(self.temp_domain_list)):
            if self.Debug: print domain
        if self.Debug: print u"\nDNSPOD带有泛解析域名如下：" if len(self.regex_domain_list)>0 else u'DNSPod带有泛解析域名：未发现'
        for domain in list(set(self.regex_domain_list)):
            if self.Debug: print domain

    def run(self):
        return self.temp_domain_list, self.regex_domain_list
