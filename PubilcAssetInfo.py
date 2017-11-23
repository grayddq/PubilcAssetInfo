# -*- coding: utf-8 -*-
import ConfigParser
from lib.Main import *

NAME, VERSION, AUTHOR, LICENSE = "Assets Info", "V0.1", "咚咚呛", "Public (FREE)"  # 版本信息

# 支持获取如下域名服务
# 1、nginx文件配置解析
# 2、腾讯云 DNSPod域名解析
# 3、阿里云 万网域名解析
# 4、百度云 BCD域名解析

# 支持公网IP获取服务
# 1、阿里云：支持ECS的专有网络、经典网络两种类型；支持SLB负载均衡服务；支持弹性公网IP服务
# 2、百度云：支持弹性公网IP服务，由于百度api的问题，其中 华东-苏州 地域不支持，等待api更新
# 3、腾讯云：支持弹性公网IP服务、CVM云服务器

if __name__ == '__main__':
    conf_info = {}
    conf = ConfigParser.ConfigParser()
    conf.read("conf/info.conf")
    # read by conf
    conf_info['Nginx_file'] = conf.get("Nginx", "Nginx_file").strip()
    conf_info['Nginx_dir'] = conf.get("Nginx", "Nginx_dir").strip()
    conf_info['AliYun_AccessKeyId'] = conf.get("AliYun", "AliYun_AccessKeyId").strip()
    conf_info['AliYun_AccessKeySecret'] = conf.get("AliYun", "AliYun_AccessKeySecret").strip()
    conf_info['DNSPod_Login_Token'] = conf.get("DNSPod", "DNSPod_Login_Token").strip()
    conf_info['BaiDuYun_AccessKey'] = conf.get("BaiDuYun", "BaiDuYun_AccessKey").strip()
    conf_info['BaiDuYun_AccessKeySecret'] = conf.get("BaiDuYun", "BaiDuYun_AccessKeySecret").strip()
    conf_info['Baidu_ROOT_Domain_List'] = conf.get("BaiDuYun", "Baidu_ROOT_Domain_List").strip().strip(',').split(',')
    conf_info['Tencent_SecretId'] = conf.get("Tencent", "Tencent_SecretId").strip()
    conf_info['Tencent_SecretKey'] = conf.get("Tencent", "Tencent_SecretKey").strip()

    conf_info['output'] = conf.get("OPTIONS", "output").strip()
    conf_info['filter_domain'] = conf.get("OPTIONS", "filter_domain").strip()
    conf_info['type'] = conf.get("OPTIONS", "type").strip()
    conf_info['logfile'] = conf.get("OPTIONS", "log").strip()
    conf_info['details_info'] = True if conf.get("OPTIONS", "details_info").strip() =='True' else False

    main(conf_info)
