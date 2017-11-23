# -*- coding: utf-8 -*-
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeEipAddressesRequest
from aliyunsdkecs.request.v20140526 import DescribeRegionsRequest
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest
import json


class AliYun_IP:
    def __init__(self, AccessKeyId, AccessKeySecret, Debug=True):
        self.AccessKeyId, self.AccessKeySecret, self.ip_list, self.regions_list = AccessKeyId, AccessKeySecret, [], []
        self.Debug = Debug
        self.get_regions()

    def get_ecs_pubilcIP(self, regions_id):
        page = 1
        errornum = 0
        while True:
            if errornum == 5: break
            try:
                clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, regions_id)
                request = DescribeInstancesRequest.DescribeInstancesRequest()
                request.set_accept_format('json')
                request.set_PageSize(100)
                request.set_PageNumber(page)  # 设置页数
                json_response = json.loads(clt.do_action_with_exception(request))
                if json_response['TotalCount'] > 0 and len(json_response['Instances']['Instance']) > 0:
                    for instance in json_response['Instances']['Instance']:
                        if len(instance['PublicIpAddress']['IpAddress']) > 0:
                            for IpAddress in instance['PublicIpAddress']['IpAddress']:
                                self.ip_list.append(IpAddress)
                        elif len(instance['EipAddress']) > 0:
                            if instance['EipAddress']['IpAddress']:
                                self.ip_list.append(instance['EipAddress']['IpAddress'])
                else:
                    break
                page += 1
            except:
                errornum += 1
                continue
        return

    def get_eip_publicIP(self, regions_id):
        page = 1
        errornum = 0
        while True:
            if errornum == 5: break
            try:
                clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, regions_id)
                request = DescribeEipAddressesRequest.DescribeEipAddressesRequest()
                request.set_accept_format('json')
                request.set_PageSize(100)
                request.set_PageNumber(page)  # 设置页数
                json_response = json.loads(clt.do_action_with_exception(request))
                if json_response['TotalCount'] > 0 and len(json_response['EipAddresses']['EipAddress']) > 0:
                    for eipaddress in json_response['EipAddresses']['EipAddress']:
                        if eipaddress['IpAddress']:
                            self.ip_list.append(eipaddress['IpAddress'])
                else:
                    break
                page += 1
            except:
                errornum += 1
                continue

    def get_slb_publicIP(self, regions_id):
        page = 1
        errornum = 0
        while True:
            if errornum == 5: break
            try:
                clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, regions_id)
                request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
                request.set_accept_format('json')
                request.set_PageSize(100)
                request.set_PageNumber(page)  # 设置页数
                request.add_query_param('RegionId', regions_id)
                json_response = json.loads(clt.do_action_with_exception(request))
                if json_response['TotalCount'] > 0 and len(json_response['LoadBalancers']['LoadBalancer']) > 0:
                    for LoadBalancer in json_response['LoadBalancers']['LoadBalancer']:
                        if LoadBalancer['Address']:
                            self.ip_list.append(LoadBalancer['Address'])
                else:
                    break
                page += 1
            except:
                errornum += 1
                continue

    # 得到地域信息
    def get_regions(self):
        clt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, 'cn-hangzhou')
        request = DescribeRegionsRequest.DescribeRegionsRequest()
        request.set_accept_format('json')
        json_response = json.loads(clt.do_action_with_exception(request))
        for regions in json_response['Regions']['Region']:
            self.regions_list.append(regions['RegionId'])
        return self.regions_list

    def run(self):
        for regions_id in self.regions_list:
            self.get_ecs_pubilcIP(regions_id)
            self.get_eip_publicIP(regions_id)
            self.get_slb_publicIP(regions_id)

        if self.Debug: print u"\n阿里云公网IP如下：" if len(self.ip_list) > 0 else u'阿里云公网IP：未发现'
        for ip in list(set(self.ip_list)):
            if self.Debug: print ip
        return list(set(self.ip_list))
