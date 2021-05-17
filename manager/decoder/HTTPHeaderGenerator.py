#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
class HTTPHeaderGenerator(object):
    @staticmethod
    def get_header_user_agent():
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0 (X11; Linux x86_64)")
        user_agent_list.append("AppleWebKit/537.36 (KHTML, like Gecko)")
        user_agent_list.append("AdvancedDownloader/0.6.0")
        return {"User-Agent": " ".join(user_agent_list)}

    @staticmethod
    def get_header_baidu_net_disk(bduss: str):
        headers = dict()
        headers["User-Agent"] = "netdisk"
        headers["Cookie"] = "BDUSS={}".format(bduss)
        return headers

    @staticmethod
    def make_dict_from_headers(content):
        each_value_list = content.split("\n")
        result_dict = {}
        for key_value in each_value_list:
            if key_value == "": continue
            key, value = key_value.split(":", 1)
            result_dict[key.strip()] = value.strip()
        return result_dict
