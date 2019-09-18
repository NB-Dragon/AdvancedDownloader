from Class.DownloadHelper import DownloadHelper
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


if __name__ == '__main__':
    url = "https://download.developer.apple.com/Developer_Tools/Xcode_10.3/Xcode_10.3.xip"
    headers = make_dict_from_headers('')
    cookies = make_dict_from_cookies('')
    download_helper = DownloadHelper(url, os.getcwd(), headers, cookies)
    download_helper.start_mission()
