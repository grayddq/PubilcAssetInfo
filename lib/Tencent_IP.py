# -*- coding: utf-8 -*-
from tencent_src.QcloudApi.qcloudapi import QcloudApi
import json
NAME, VERSION, AUTHOR, LICENSE = "Assets Info", "V0.1", "咚咚呛", "Public (FREE)"  # 版本信息

class Tencent_IP:
    def __init__(self, AccessKeyId, AccessKeySecret, Debug=True):
        self.AccessKeyId, self.AccessKeySecret, self.ip_list, self.Region_list = AccessKeyId, AccessKeySecret, [], []
        self.Debug = Debug
        self.get_region_list()

    def get_region_list(self):
        config = {
            'Region': 'ap-beijing',
            'secretId': self.AccessKeyId,
            'secretKey': self.AccessKeySecret,
            'method': 'get'
        }
        service = QcloudApi('cvm', config)
        service.generateUrl('DescribeRegions', {})
        json_response = json.loads(service.call('DescribeRegions', {}))
        for region in json_response['regionSet']:
            self.Region_list.append(region['region'])

    def get_eip(self, Region, limit=100):
        offset, errornum = 0, 0
        while True:
            if errornum == 5: break
            try:
                config = {
                    'Region': Region,
                    'secretId': self.AccessKeyId,
                    'secretKey': self.AccessKeySecret,
                    'method': 'get'
                }
                service = QcloudApi('eip', config)
                service.generateUrl('DescribeEip', {'limit': limit, 'offset': offset})
                json_response = json.loads(service.call('DescribeEip', {'limit': limit, 'offset': offset}))
                if json_response['codeDesc'] == 'Success':
                    if json_response['totalCount'] > 0 and len(json_response['data']['eipSet']) > 0:
                        for eipSet in json_response['data']['eipSet']:
                            if eipSet['eip']: self.ip_list.append(eipSet['eip'])
                        if len(json_response['data']['eipSet']) == limit:
                            offset += limit
                            continue
                break
            except:
                errornum += 1
                continue

    def get_cvm(self, Region, limit=100):
        offset, errornum = 0, 0
        while True:
            if errornum == 5: break
            try:
                config = {
                    'Region': Region,
                    'secretId': self.AccessKeyId,
                    'secretKey': self.AccessKeySecret,
                    'method': 'get'
                }
                service = QcloudApi('cvm', config)
                service.generateUrl('DescribeInstances', {'limit': limit, 'offset': offset})
                json_response = json.loads(service.call('DescribeInstances', {'limit': limit, 'offset': offset}))
                if json_response['codeDesc'] == 'Success':
                    if json_response['totalCount'] > 0 and len(json_response['instanceSet']) > 0:
                        for instanceSet in json_response['instanceSet']:
                            for wanIpSet in instanceSet['wanIpSet']:
                                self.ip_list.append(wanIpSet)
                        if len(json_response['instanceSet']) == limit:
                            offset += limit
                            continue
                break
            except:
                errornum += 1
                continue

    def run(self):
        for Region in self.Region_list:
            self.get_eip(Region)
            self.get_cvm(Region)

        if self.Debug: print u"\n腾讯云公网IP如下：" if len(self.ip_list) > 0 else u'腾讯云公网IP：未发现'
        for ip in list(set(self.ip_list)):
            if self.Debug: print ip

        return list(set(self.ip_list))
