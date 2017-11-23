# -*- coding: utf-8 -*-
from aliyunsdkcore import client
from aliyunsdkcore.request import RpcRequest
import json


# 获取阿里域名列表
class AliYunDns_doamin:
    def __init__(self, AccessKeyId, AccessKeySecret, filter_domain, Debug=True):
        self.domain_list, self.temp_domain_list, self.regex_domain_list = [], [], []
        self.AccessKeyId, self.AccessKeySecret = AccessKeyId, AccessKeySecret
        self.filter_domain = '' if not filter_domain else filter_domain
        self.Debug = Debug
        self.get_domain()

    def get_reslut(self, type, domain=None, PageNumber=1):
        try:
            clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, 'cn-shanghai')
            if type == "domain":
                request = RpcRequest('Alidns', '2015-01-09', 'DescribeDomains')
                request.add_query_param("PageSize", 100)
            else:
                request = RpcRequest('Alidns', '2015-01-09', 'DescribeDomainRecords')
                request.add_query_param("DomainName", domain)
                request.add_query_param("PageSize", 500)
                request.add_query_param("PageNumber", PageNumber)
            request.set_accept_format('json')
            json_response = json.loads(clt.do_action_with_exception(request))
        except:
            json_response = None
        return json_response

    def get_domain(self):
        response = self.get_reslut('domain')
        if response == None: return
        if response['TotalCount'] > 0:
            for data in response['Domains']['Domain']:
                page = 1
                while True:
                    if page == 10: break
                    sub_response = self.get_reslut('sub_domain', data['DomainName'], page)
                    if sub_response == None: continue
                    if sub_response['TotalCount'] > 0 and len(sub_response['DomainRecords']['Record']) > 0:
                        for records_data in sub_response['DomainRecords']['Record']:
                            if records_data['Type'] in ['A', 'CNAME'] and records_data['RR'] != '@' and records_data[
                                'Status'] == 'ENABLE':
                                if records_data['RR'].replace('.', '').isalnum():
                                    self.temp_domain_list.append(records_data['RR'] + "." + records_data['DomainName'])
                                else:
                                    self.regex_domain_list.append(records_data['RR'] + "." + records_data['DomainName'])
                    else:
                        break
                    page += 1
        self.domain_list = self.temp_domain_list + self.regex_domain_list


    def run(self):
        if self.Debug: print u"\n阿里云常规DNS解析域名如下：" if len(self.temp_domain_list)>0 else u'阿里云常规DNS解析域名：未发现'
        for domain in list(set(self.temp_domain_list)):
            if self.Debug: print domain
        if self.Debug: print u"\n阿里云DNS解析带有泛解析域名如下：" if len(self.regex_domain_list) > 0 else u'阿里云DNS带有泛解析域名：未发现'
        for domain in list(set(self.regex_domain_list)):
            if self.Debug: print domain
        return self.temp_domain_list, self.regex_domain_list
