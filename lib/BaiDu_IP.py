# -*- coding: utf-8 -*-
import urllib, json, hmac, hashlib, urllib2
from datetime import datetime


# 百度域名获取
class BaiDu_IP:
    def __init__(self, AccessKeyId, AccessKeySecret, Debug=True):
        self.AccessKeyId, self.AccessKeySecret, self.ip_list = AccessKeyId, AccessKeySecret, []
        # 弹性公网IP暂时支持两个两个区域：华南-广州、华北-北京
        self.Region_list = ['eip.bj.baidubce.com', 'eip.gz.baidubce.com']
        self.Debug = Debug

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
        time_bce = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # 自行评估哪些header会出现在提交的请求内，继而在此对这些headers进行声明
        req_headers = {'Host': conf['host'],
                       'Content-Type': conf['contentType'],
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

    def get_reslut(self, host, marker=''):
        conf = {'ak': self.AccessKeyId,
                'sk': self.AccessKeySecret,
                'host': '%s' % host,
                'protocol': 'http',
                'method': 'get',
                'path': '/v1/eip',
                'auth_version': 'bce-auth-v1',
                'contentType': 'application/json'
                }
        body_post = {}
        payload = json.dumps(body_post)
        querystring = 'maxKeys=1' if not marker else 'marker=%s&maxKeys=1' % marker
        token_obj = self.get_headers_with_auth(conf, payload, querystring)

        url = "http://%s/v1/eip?maxKeys=1" % host if not marker else "http://%s/v1/eip?marker=%s&maxKeys=1" % (
            host, marker)
        send_headers = {
            'Host': '%s' % host,
            'x-bce-date': '%s' % token_obj['x-bce-date'],
            'Authorization': '%s' % token_obj['Authorization'],
            'Content-Type': 'application/json'
        }
        try:
            request = urllib2.Request(url, headers=send_headers)
            json_response = json.loads(urllib2.urlopen(request).read())
        except:
            json_response = None
        return json_response

    def get_ip(self):
        for Region in self.Region_list:
            marker, errornum = '', 0
            while True:
                if errornum == 5: break
                json_response = self.get_reslut(Region, marker)
                if json_response:
                    if len(json_response['eipList']) > 0:
                        for eipList in json_response['eipList']:
                            self.ip_list.append(eipList['eip'])
                    if json_response['isTruncated']:
                        marker = json_response['nextMarke']
                    else:
                        break
                else:
                    errornum += 1

    def run(self):
        self.get_ip()
        if self.Debug: print u"\n百度云公网IP如下：" if len(self.ip_list) > 0 else u'百度云公网IP：未发现'
        for ip in list(set(self.ip_list)):
            if self.Debug: print ip
        return self.ip_list
