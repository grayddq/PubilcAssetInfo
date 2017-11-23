# -*- coding: utf-8 -*-
import urllib, json, hmac, hashlib, urllib2
from datetime import datetime


# 百度域名获取
class BaiDu_BCD_domain:
    def __init__(self, AccessKeyId, AccessKeySecret, root_domain_list, filter_domain=None, Debug=True):
        self.domain_list, self.temp_domain_list, self.regex_domain_list = [], [], []
        self.AccessKeyId, self.AccessKeySecret, self.root_domain_list = AccessKeyId, AccessKeySecret, root_domain_list
        self.Debug = Debug
        self.filter_domain = '' if not filter_domain else filter_domain

    def digest(self, key, msg):
        """消息摘要算法（加盐）"""
        digester = hmac.new(key, msg, hashlib.sha256)
        HMAC_SHA256 = digester.hexdigest()
        return HMAC_SHA256

    def querystring_be_canonical(self, string):
        """
        test case
        string = 'text&text1=测试&text10=test'
        string = ''
        """
        if string != '':
            lst = string.split('&')
            string_lst = []
            for i in lst:

                if '=' in i:
                    string_lst.append(urllib.quote(i, safe='='))
                else:
                    string_lst.append(urllib.quote(i, safe='') + '=')

            string_lst.sort()
            qs_canonical = '&'.join(string_lst)
        else:
            qs_canonical = ''

        return qs_canonical

    def headers_be_canonical(self, headers):
        keys = []
        items = []

        for k, v in headers.items():
            keys.append(k.lower())

            item = "{}:{}".format(urllib.quote(k.lower(), safe=''), urllib.quote(v.strip(), safe=''))
            items.append(item)

        # "注意相关举例2： CanonicalHeaders的排序和signedHeaders排序不一致。"
        keys.sort()
        keys = ';'.join(keys)

        items.sort()
        headers_plain = '\n'.join(items)

        return keys, headers_plain

    def get_headers_with_auth(self, conf, payload, querystring):
        contentLength = str(len(payload))
        time_bce = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # 自行评估哪些header会出现在提交的请求内，继而在此对这些headers进行声明
        req_headers = {'Host': conf['host'],
                       'Content-Type': conf['contentType'],
                       'Content-Length': contentLength,
                       'x-bce-date': time_bce
                       }

        # 获取已编码并扁平化的Headers字串
        headers_signed, headers_canonical = self.headers_be_canonical(req_headers)

        # 对请求的资源路径编码
        uri_canonical = urllib.quote(conf['path'], safe='/')

        # 对请求携带的查询参数编码
        querystring_canonical = self.querystring_be_canonical(querystring)

        # 构造合规化请求字串
        request_canonical = '\n'.join([conf['method'].upper(), uri_canonical, querystring_canonical, headers_canonical])

        # 认证字串前缀
        authStringPrefix = conf['auth_version'] + '/' + conf['ak'] + '/' + time_bce + '/' + '1800'

        # 摘要算法需用到的key
        signing_key = self.digest(conf['sk'], authStringPrefix)

        # 摘要
        signature = self.digest(signing_key, request_canonical)

        # 构造认证字串(显式声明已参与签名的所有header，而非采用由百度定义的缺省方式)
        authorization = authStringPrefix + '/' + headers_signed + '/' + signature

        # 为原始请求headers附加认证字串header
        req_headers['Authorization'] = authorization

        return req_headers

    def get_sub_reslut(self, root_domain, pageNo=1, pageSize=100):
        conf = {'ak': self.AccessKeyId,
                'sk': self.AccessKeySecret,
                'host': 'bcd.baidubce.com',
                'protocol': 'http',
                'method': 'post',
                'path': '/v1/domain/resolve/list',
                'auth_version': 'bce-auth-v1',
                'contentType': 'application/json'
                }
        domain = {
            'domain': '%s' % root_domain,
            'pageNo': pageNo,
            'pageSize': pageSize
        }
        payload = json.dumps(domain)
        querystring = ''
        token_obj = self.get_headers_with_auth(conf, payload, querystring)

        url = "http://bcd.baidubce.com/v1/domain/resolve/list"
        send_headers = {
            'Host': 'bcd.baidubce.com',
            'x-bce-date': '%s' % token_obj['x-bce-date'],
            'Authorization': '%s' % token_obj['Authorization'],
            'Content-Type': 'application/json'
        }
        try:
            request = urllib2.Request(url, data=payload, headers=send_headers)
            json_response = json.loads(urllib2.urlopen(request).read())
        except:
            json_response = None
        return json_response

    def get_sub_domain(self, domain):
        page = 1
        while True:
            if page == 10: break
            json_response = self.get_sub_reslut(domain, page, 100)
            if json_response == None: return
            if json_response['totalCount'] > 0 and len(json_response['result']) > 0:
                for data in json_response['result']:
                    if data['rdtype'] in ['A', 'CNAME'] and data['domain'] != '@' and data['status'] == 'RUNNING':
                        if data['domain'].replace('.', '').isalnum():
                            self.temp_domain_list.append(data['domain'] + '.' + data['zoneName'])
                        else:
                            self.regex_domain_list.append(data['domain'] + '.' + data['zoneName'])
            else:
                break
            page += 1

    def run(self):
        for domain in self.root_domain_list:
            self.get_sub_domain(domain)
        self.domain_list = self.temp_domain_list + self.regex_domain_list

        if self.Debug: print u"\n百度云常规DNS解析域名如下：" if len(self.temp_domain_list) > 0 else u'百度云常规DNS解析域名：未发现'
        for domain in list(set(self.temp_domain_list)):
            if self.Debug: print domain
        if self.Debug: print u"\n百度云DNS带有泛解析域名如下：" if len(self.regex_domain_list) > 0 else u'百度云DNS带有泛解析域名：未发现'
        for domain in list(set(self.regex_domain_list)):
            if self.Debug: print domain

        return self.temp_domain_list, self.regex_domain_list
