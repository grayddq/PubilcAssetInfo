# -*- coding: utf-8 -*-
import datetime, os
from AliYunDns_doamin import *
from DNSPod import *
from Nginx_Server_Name import *
from BaiDu_BCD_domain import *
from AliYun_IP import *
from BaiDu_IP import *
from Tencent_IP import *
from Log import *

NAME, VERSION, AUTHOR, LICENSE = "Assets Info", "V0.1", "咚咚呛", "Public (FREE)"  # 版本信息


def main(conf_info):
    domain_list, temp_domain_list, regex_domain_list, ip_list = [], [], [], []
    if not os.path.exists('out'):
        os.mkdir('out')
    if not os.path.exists('log'):
        os.mkdir('log')

    outfile = 'out/' + str(datetime.now().strftime('%Y-%m-%d_%H_%M_%S')) + 'info.txt' if not conf_info[
        'output'] else conf_info['output']
    logger = LogInfo('%s' % conf_info['logfile'] if conf_info['logfile'] else 'log/process.log')
    logger.infostring('read conf success')
    if not conf_info['type'] or conf_info['type'] == 'domain':
        if conf_info['Nginx_file'] or conf_info['Nginx_dir']:
            logger.infostring(
                'start analysis nginx file/dir: %s...' % conf_info['Nginx_file'] if conf_info['Nginx_file'] else
                conf_info[
                    'Nginx_dir'])
            temp_nginx_domain, temp_nginx_regex = Nginx_Server_Name(conf_info['Nginx_dir'],
                                                                    conf_info['filter_domain'],
                                                                    Debug=conf_info['details_info']
                                                                    ).run() if conf_info[
                'Nginx_dir'] else Nginx_Server_Name(conf_info['Nginx_file'],
                                                    conf_info['filter_domain'],
                                                    Debug=conf_info['details_info']
                                                    ).run()
            temp_domain_list += temp_nginx_domain
            regex_domain_list += temp_nginx_regex
            logger.infostring(
                'finsh nginx dns parsing,find conventional domain num: %d, regular expression domain num: %d' % (
                    len(temp_nginx_domain), len(temp_nginx_regex)))

        if conf_info['DNSPod_Login_Token']:
            logger.infostring('start analysis dnspod dns parsing...')
            temp_dnspod_domain, temp_dnspod_regex = DNSPod_domain(conf_info['DNSPod_Login_Token'],
                                                                  conf_info['filter_domain'],
                                                                  Debug=conf_info['details_info']
                                                                  ).run()
            temp_domain_list += temp_dnspod_domain
            regex_domain_list += temp_dnspod_regex
            logger.infostring(
                'finsh dnspod dns parsing,find conventional domain num: %d, regular expression domain num: %d' % (
                    len(temp_dnspod_domain), len(temp_dnspod_regex)))

        if conf_info['AliYun_AccessKeySecret']:
            logger.infostring('start analysis ali cloud dns parsing...')
            temp_aliyun_domain, temp_aliyun_regex = AliYunDns_doamin(conf_info['AliYun_AccessKeyId'],
                                                                     conf_info['AliYun_AccessKeySecret'],
                                                                     conf_info['filter_domain'],
                                                                     Debug=conf_info['details_info']
                                                                     ).run()
            temp_domain_list += temp_aliyun_domain
            regex_domain_list += temp_aliyun_regex
            logger.infostring(
                'finsh dnspod dns parsing,conventional domain num: %d, regular expression domain num: %d' % (
                    len(temp_aliyun_domain), len(temp_aliyun_regex)))

        if conf_info['BaiDuYun_AccessKey']:
            logger.infostring('start analysis baidu cloud dns parsing...')
            temp_baiduyun_domain, temp_baiduyun_regex = BaiDu_BCD_domain(conf_info['BaiDuYun_AccessKey'],
                                                                         conf_info['BaiDuYun_AccessKeySecret'],
                                                                         conf_info['Baidu_ROOT_Domain_List'],
                                                                         conf_info['filter_domain'],
                                                                         Debug=conf_info['details_info']
                                                                         ).run()
            temp_domain_list += temp_baiduyun_domain
            regex_domain_list += temp_baiduyun_regex
            logger.infostring(
                'finsh baidu dns parsing,conventional domain num: %d, regular expression domain num: %d' % (
                    len(temp_baiduyun_domain), len(temp_baiduyun_regex)))
    if not conf_info['type'] or conf_info['type'] == 'ip':
        if conf_info['AliYun_AccessKeySecret']:
            logger.infostring('start analysis ali cloud public ip...')
            temp_ip_list = AliYun_IP(conf_info['AliYun_AccessKeyId'],
                                     conf_info['AliYun_AccessKeySecret'],
                                     Debug=conf_info['details_info']
                                     ).run()
            ip_list += temp_ip_list
            logger.infostring('finsh ali public ip,num: %d' % (len(temp_ip_list)))

        if conf_info['BaiDuYun_AccessKeySecret']:
            logger.infostring('start analysis baidu cloud public ip...')
            temp_ip_list = BaiDu_IP(conf_info['BaiDuYun_AccessKey'],
                                    conf_info['BaiDuYun_AccessKeySecret'],
                                    Debug=conf_info['details_info']
                                    ).run()
            ip_list += temp_ip_list
            logger.infostring('finsh baidu public ip,num: %d' % (len(temp_ip_list)))

        if conf_info['Tencent_SecretKey']:
            logger.infostring('start analysis tencent cloud public ip...')
            temp_ip_list = Tencent_IP(conf_info['Tencent_SecretId'],
                                      conf_info['Tencent_SecretKey'],
                                      Debug=conf_info['details_info']
                                      ).run()
            ip_list += temp_ip_list
            logger.infostring('finsh tencent public ip,num: %d' % (len(temp_ip_list)))

    out = open(outfile, 'w')
    if conf_info['type'] != 'ip': out.write("完整域名如下\n")
    for domain in list(set(temp_domain_list)):
        out.write(domain + "\n")
    if conf_info['type'] != 'ip': out.write("\n带有正则或者通配符域名如下\n")
    for domain in list(set(regex_domain_list)):
        out.write(domain + "\n")
    if conf_info['type'] != 'ip': out.write("\nIP信息如下\n")
    for ip in list(set(ip_list)):
        out.write(ip + "\n")
    out.close()
    logger.infostring('Finsh current task, Domain: %d, IP: %d, results path: %s' % (
        len(list(set(temp_domain_list)) + list(set(regex_domain_list))), len(ip_list), outfile))
