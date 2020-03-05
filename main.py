from Class.DownloadHelper import DownloadHelper
from Class.MessageHandler import MessageHandler
import os


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


if __name__ == '__main__':
    url = "https://lipn.univ-paris13.fr/~dam/tool/androidTool/MADLIRA_.7z"
    headers = make_dict_from_headers('')
    cookies = make_dict_from_cookies('')
    message_listener = start_message_listener()
    download_helper = DownloadHelper(message_listener.get_message_queue(), url, os.getcwd(), headers, cookies)
    message_listener.send_stop_state()
