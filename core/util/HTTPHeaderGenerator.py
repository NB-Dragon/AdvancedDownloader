#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import re


class HTTPHeaderGenerator(object):
    def __init__(self, version_name: str):
        self._version_name = version_name
        self._init_application_user_agent()

    def _init_application_user_agent(self):
        self._application_user_agent = "AdvancedDownloader/{}".format(self._version_name)

    def generate_header_with_default_agent(self):
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0 (X11; Linux x86_64)")
        user_agent_list.append("AppleWebKit/537.36 (KHTML, like Gecko)")
        user_agent_list.append(self._application_user_agent)
        return {"User-Agent": " ".join(user_agent_list)}

    def generate_header_from_content(self, header_content):
        each_value_list = header_content.split("\n")
        result_dict = {}
        for key_value in each_value_list:
            if ":" in key_value:
                key, value = key_value.split(":", 1)
                result_dict[key.strip()] = value.strip()
        if self._judge_baidu_disk_request(result_dict):
            result_dict["User-Agent"] = "netdisk"
        return result_dict

    @staticmethod
    def _judge_baidu_disk_request(headers: dict):
        return len(re.findall("BDUSS=[^;]+", headers["Cookie"])) > 0 if "Cookie" in headers else False
