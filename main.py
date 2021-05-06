#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/20 10:00
# Create User: anonymous
import os
from tools.DownloadHelper import DownloadHelper
from tools.RuntimeOperator import RuntimeOperator
from schema.analyser.HTTPHelper import HeaderGenerator
from listener.ThreadMessageDistributor import ThreadMessageDistributor

if __name__ == '__main__':
    runtime_operator = RuntimeOperator()
    thread_message_distributor = ThreadMessageDistributor(runtime_operator)
    thread_message_queue = thread_message_distributor.get_message_queue()
    thread_message_distributor.start()
    download_helper = DownloadHelper(thread_message_queue, runtime_operator)

    headers = HeaderGenerator.get_header_user_agent()
    # url = "https://vipspeedtest1.wuhan.net.cn:8080/download?size=25000000&r=0.5588543787999258"
    url = "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/tags/v0.5.9.zip"
    base_info = {"download_link": url, "save_path": os.getcwd(), "thread_num": 32, "headers": headers}
    download_helper.create_download_mission(base_info)

    thread_message_distributor.send_stop_state()
