#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/20 10:00
# Create User: anonymous
import os
from tool.DownloadHelper import DownloadHelper
from tool.RuntimeOperator import RuntimeOperator
from schema.RequestDictionary import RequestDictionary
from listener.ThreadMessageDistributor import ThreadMessageDistributor

if __name__ == '__main__':
    runtime_operator = RuntimeOperator()

    thread_message_distributor = ThreadMessageDistributor(runtime_operator)
    thread_message_queue = thread_message_distributor.get_message_queue()
    thread_message_distributor.start()
    download_helper = DownloadHelper(thread_message_queue)

    headers = RequestDictionary.make_dict_from_headers("")
    cookies = RequestDictionary.make_dict_from_cookies("")
    url = "https://gdspeedtest.com.prod.hosts.ooklaserver.net:8080/download?size=25000000"
    # url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.5.0/apktool_2.5.0.jar"
    base_info = {"download_link": url, "save_path": os.getcwd(), "thread_num": 128}
    base_info.update({"headers": headers, "cookies": cookies})
    download_helper.create_new_download_mission(base_info)

    thread_message_distributor.send_stop_state()
