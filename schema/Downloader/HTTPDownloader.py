import os
import queue
import requests
from schema.Analyser.HTTPHelper import HTTPHelper


class HTTPDownloader(object):
    def __init__(self, mission_uuid, mission_info: dict, download_info: dict, thread_message: queue.Queue):
        self._mission_uuid = mission_uuid
        self._mission_info = mission_info
        # mission_info = {"download_link": str, "save_path": str, "thread_num": 128, "headers": dict, "cookies": dict}
        self._thread_message = thread_message
        self._download_config = download_info
        # download_info = {"file_info": dict, "all_region": list[tuple], "tmp_path": str}

    def start_download_mission(self):
        self._try_to_update_mission_info()
        if self._download_config["file_info"]:
            self._create_download_tmp_file()
            # do something here
            self._rename_final_save_file()
        else:
            self._make_message_and_send("资源禁止访问，请确认验证信息", False)

    def _try_to_update_mission_info(self):
        if len(self._download_config) == 0:
            self._download_config["file_info"] = self._analyse_target_file_info()
            self._download_config["all_region"] = self._generate_file_all_region(self._download_config["file_info"])
            self._download_config["tmp_path"] = self._generate_tmp_file_path(self._download_config["file_info"])

    def _create_download_tmp_file(self):
        self._make_message_and_send("文件正在初始化", False)
        writer = open(self._download_config["tmp_path"], 'a+b')
        file_size = self._download_config["file_info"]["filesize"]
        file_buff = self._get_empty_byte_array(self._download_config["tmp_path"], file_size)
        writer.write(file_buff)
        writer.close()

    def _rename_final_save_file(self):
        self._make_message_and_send("文件正在进行整合", False)
        file_info = self._download_config["file_info"]
        save_file = os.path.join(self._mission_info["save_path"], file_info["filename"])
        os.rename(self._download_config["tmp_path"], save_file)

    def _analyse_target_file_info(self):
        tmp_headers = self._mission_info["headers"].copy()
        tmp_headers["Range"] = "bytes=0-0"
        tmp_cookies = self._mission_info["cookies"].copy()
        for try_time in range(3):
            stream_response = self._get_simple_response(self._mission_info["download_link"], tmp_headers, tmp_cookies)
            if self._check_response_can_access(stream_response):
                headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
                stream_response.close()
                file_info = HTTPHelper.get_download_file_requirement(headers, self._mission_info["download_link"])
                if file_info["range"] or try_time == 2:
                    return file_info
        return None

    def _generate_file_all_region(self, file_info):
        if file_info and file_info["range"]:
            return HTTPHelper.get_download_region([(0, file_info["filesize"])], self._mission_info["thread_num"])
        else:
            return [(0,)]

    def _generate_tmp_file_path(self, file_info):
        if file_info:
            file_name = "{}.tmp".format(file_info["filename"])
            return os.path.join(self._mission_info["save_path"], file_name)
        else:
            return None

    @staticmethod
    def _get_empty_byte_array(file_path, expect_size):
        if isinstance(expect_size, int):
            current_file_size = os.path.getsize(file_path)
            return bytearray(expect_size - current_file_size)
        else:
            return bytearray(0)

    @staticmethod
    def _check_response_can_access(stream_response):
        if stream_response is None:
            return False
        if stream_response.status_code in [200, 206]:
            return True
        else:
            stream_response.close()
            return False

    def _get_simple_response(self, target_url, headers, cookies):
        try:
            return requests.get(target_url, stream=True, timeout=10, headers=headers, cookies=cookies)
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "HTTPDownloader", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)
