import os
import time
from Class.DownloadHelper import DownloadHelper
from Class.MessageReceiveThread import MessageReceiveThread


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
    message_receiver = MessageReceiveThread()
    message_receiver.start()
    return message_receiver


if __name__ == '__main__':
    headers = make_dict_from_headers('')
    cookies = make_dict_from_cookies('')
    url = "https://github.com/tensorflow/tensorflow/archive/master.zip"
    message_receiver = start_message_listener()
    message_queue = message_receiver.get_message_queue()

    save_path = os.getcwd()
    download_index = int(time.time() * 1000000)

    download_helper = DownloadHelper(message_queue, url, save_path, download_index, headers, cookies)
    message_receiver.send_stop_state()
