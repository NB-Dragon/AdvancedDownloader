#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/20 10:00
# Create User: anonymous
import os
from tool.DownloadHelper import DownloadHelper
from tool.FileOpenHelper import FileOpenHelper
from tool.RuntimeOperator import RuntimeOperator
from schema.RequestDictionary import RequestDictionary
from listener.ThreadMessageDistributor import ThreadMessageDistributor

if __name__ == '__main__':
    runtime_operator = RuntimeOperator()
    thread_message_distributor = ThreadMessageDistributor(runtime_operator)
    thread_message_queue = thread_message_distributor.get_message_queue()
    thread_message_distributor.start()
    download_helper = DownloadHelper(thread_message_queue)
    file_open_helper = FileOpenHelper(thread_message_queue)

    headers = RequestDictionary.make_dict_from_headers("")
    # url = "https://vipspeedtest1.wuhan.net.cn:8080/download?size=25000000&r=0.5588543787999258"
    url = "https://github.com/iBotPeaches/Apktool/releases/download/v2.5.0/apktool_2.5.0.jar"
    base_info = {"download_link": url, "save_path": os.getcwd(), "thread_num": 128, "headers": headers}
    download_helper.create_download_mission(base_info)

    file_open_helper.open(runtime_operator.get_donate_image_path())
    thread_message_distributor.send_stop_state()
