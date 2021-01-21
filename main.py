#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/20 10:00
# Create User: anonymous

import os
from tool.DownloadHelper import DownloadHelper
from schema.RequestDictionary import RequestDictionary
from listener.ThreadMessageDistributor import ThreadMessageDistributor
from tool.RuntimeOperator import RuntimeOperator

if __name__ == '__main__':
    runtime_operator = RuntimeOperator()

    thread_message_distributor = ThreadMessageDistributor(runtime_operator)
    thread_message_queue = thread_message_distributor.get_message_queue()
    thread_message_distributor.start()

    headers = RequestDictionary.make_dict_from_headers("")
    cookies = RequestDictionary.make_dict_from_cookies("")
    # url = "https://speedtest3.gd.chinamobile.com.prod.hosts.ooklaserver.net:8080/download?size=1073741824"
    url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.5.0/apktool_2.5.0.jar"
    DownloadHelper(thread_message_queue, url, os.getcwd(), headers, cookies)

    thread_message_distributor.send_stop_state()
