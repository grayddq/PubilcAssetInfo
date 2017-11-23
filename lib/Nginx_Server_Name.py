# -*- coding: utf-8 -*-
import re, os


class Nginx_Server_Name:
    def __init__(self, target, filter_domain, Debug=True):
        self.target, self.conf_list, self.domain_list, self.temp_domain_list, self.regex_domain_list = target, [], [], [], []
        self.filter_domain = '' if not filter_domain else filter_domain
        self.Debug = Debug

    def run(self):
        self.get_conf_list()
        return self.temp_domain_list, self.regex_domain_list

    def get_conf_list(self):
        if not os.path.exists(self.target): return
        if os.path.isfile(self.target):
            self.conf_list.append(self.target)
        else:
            for path, d, filelist in os.walk(self.target):
                for filename in filelist:
                    if os.path.splitext(filename)[1] == '.conf': self.conf_list.append(os.path.join(path, filename))
        for file in self.conf_list:
            server_list, re_list = self.get_domain(file, self.filter_domain)
            self.temp_domain_list += server_list
            self.regex_domain_list += re_list
        self.domain_list = list(set(self.temp_domain_list)) + list(set(self.regex_domain_list))

        if self.Debug:
            print u"\nNginx非正则域名如下：" if len(self.temp_domain_list) > 0 else u'Nginx非正则域名：未发现'
        for domain in list(set(self.temp_domain_list)):
            if self.Debug: print domain
        if self.Debug:
            print u"\nNginx正则或通配符域名如下：" if len(self.regex_domain_list) > 0 else u'Nginx正则或通配符域名：未发现'
        for domain in list(set(self.regex_domain_list)):
            if self.Debug: print domain

    # 获取指定conf文件的server_name
    # file 文件绝对路径
    # 输出两个list
    #   server_list：绝对域名列表
    #   re_list：带有正则或者通配符的域名
    def get_domain(self, file, filter_domain):
        server_list, re_list = [], []  # 域名
        f = open(file, 'rb')
        try:
            for line in f:
                if re.compile('server_name').search(line.strip()):
                    l = ' '.join(line.strip().split())  # 去掉多余空格和tab
                    if not l.replace(' ', '').lower().startswith('server_name'): continue
                    domain_list = re.split(' +|;', l)
                    for domain in domain_list:
                        if not domain.lower() in ['', 'localhost', 'server_name']:
                            # nginx 配置中如果server_name需要填写正则，则第一个字符必然为 ～
                            # 存在带有~^xxxx.xxx.com这样写域名的写法，匹配除了~ ^ .其他特殊符都为正则匹配
                            if domain.replace('~', '').replace('^', '').replace('.', '').isalnum():
                                if filter_domain in domain: server_list.append(domain.replace('~', '').replace('^', ''))
                            else:
                                if filter_domain in domain: re_list.append(domain)
            f.close()
        except:
            f.close()
        return server_list, re_list
