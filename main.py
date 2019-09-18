from Class.DownloadHelper import DownloadHelper
import os


def make_dict_from_content(content):
    each_value_list = content.split(";")
    result_dict = {}
    for key_value in each_value_list:
        if key_value == "": continue
        key, value = key_value.split("=", 1)
        result_dict[key.strip()] = value.strip()
    return result_dict


if __name__ == '__main__':
    url = "https://download.sj.qq.com/upload/QQphonemanger/5-8-1/QQPhoneManager_990420.5239.exe"
    headers = make_dict_from_content('')
    cookies = make_dict_from_content('')
    download_helper = DownloadHelper(url, os.getcwd(), headers, cookies)
    download_helper.start_mission()
