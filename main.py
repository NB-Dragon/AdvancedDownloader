from Class.DownloadHelper import DownloadHelper
from Class.MessageHandler import MessageHandler
import os
import time


def make_dict_from_cookies(content):
    each_value_list = content.split(";")
    result_dict = {}
    for key_value in each_value_list:
        if key_value == "": continue
        key, value = key_value.split("=", 1)
        result_dict[key.strip()] = value.strip()
    return result_dict


def make_dict_from_headers(content):
    each_value_list = content.split("\n")
    result_dict = {}
    for key_value in each_value_list:
        if key_value == "": continue
        key, value = key_value.split(":", 1)
        result_dict[key.strip()] = value.strip()
    return result_dict


def start_message_listener():
    message_handler = MessageHandler()
    message_handler.start()
    return message_handler


def check_use_time():
    print("你当前使用的工具为试用版，请尽快购买，以保障工具的正常使用")
    limit_use_time = "2020-03-08 00:00:00"
    time_format_string = "%Y-%m-%d %H:%M:%S"
    limit_use_time_stamp = time.mktime(time.strptime(limit_use_time, time_format_string))
    time_length = limit_use_time_stamp - time.time()
    if time_length <= 0:
        print("工具已过有效期，请充值后使用")
        exit()
    else:
        print("本工具将在{}失效".format(limit_use_time))


if __name__ == '__main__':
    check_use_time()
    url = "https://codeload.github.com/MobSF/Mobile-Security-Framework-MobSF/tar.gz/v3.0.1"
    headers = make_dict_from_headers('')
    cookies = make_dict_from_cookies('')
    message_listener = start_message_listener()
    download_helper = DownloadHelper(message_listener.get_message_queue(), url, os.getcwd(), headers, cookies)
    message_listener.send_stop_state()
