#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import os
import queue
import urllib3
import threading
from schema.RegionMaker import RegionMaker
from schema.Analyser.HTTPHelper import HTTPHelper


class HTTPDownloader(object):
    def __init__(self, mission_uuid, mission_info: dict, download_info: dict, thread_message: queue.Queue):
        self._mission_uuid = mission_uuid
        self._mission_info = mission_info
        # mission_info = {"download_link": str, "save_path": str, "thread_num": 128, "headers": dict}
        self._download_info = download_info
        # download_info = {"file_info": dict, "all_region": list[list], "tmp_path": str}
        self._thread_message = thread_message
        self._request_pool = self._init_request_pool()
        self._mission_lock = self._init_mission_lock()

        self._free_worker_count = self._mission_info["thread_num"]
        self._download_thread_message = queue.Queue()

    def start_download_mission(self):
        self._encode_mission_info()
        self._try_to_update_mission_info()
        if self._download_info["file_info"]:
            self._create_download_tmp_file()
            self._send_download_mission_register()
            self._create_download_mission(self._download_info["all_region"])
            self._listen_download_message()
            self._mission_lock.acquire()
            self._rename_final_save_file()
            self._mission_lock.release()
        else:
            self._make_message_and_send("资源禁止访问，请确认验证信息", False)

    def _init_request_pool(self):
        thread_count = self._mission_info["thread_num"]
        return HTTPHelper.get_request_pool_manager(thread_count)

    @staticmethod
    def _init_mission_lock():
        lock = threading.Lock()
        lock.acquire()
        return lock

    def _encode_mission_info(self):
        download_link = self._mission_info["download_link"]
        self._mission_info["download_link"] = HTTPHelper.get_url_after_quote(download_link)

    def _try_to_update_mission_info(self):
        self._make_message_and_send("资源连接中", False)
        if len(self._download_info) == 0 or self._download_info["file_info"]["range"] is False:
            self._download_info["file_info"] = self._analyse_target_file_info()
            self._download_info["all_region"] = self._generate_file_all_region(self._download_info["file_info"])
            self._download_info["tmp_path"] = self._generate_tmp_file_path(self._download_info["file_info"])
        self._make_message_and_send("资源解析完成", False)

    def _create_download_tmp_file(self):
        self._make_message_and_send("任务正在初始化", False)
        writer = open(self._download_info["tmp_path"], 'a+b')
        expect_size = self._download_info["file_info"]["filesize"]
        if isinstance(expect_size, int):
            current_size = os.path.getsize(self._download_info["tmp_path"])
            byte_buffer_65536 = bytearray(65536)
            for index in range((expect_size - current_size) // 65536):
                writer.write(byte_buffer_65536)
            writer.write(bytearray((expect_size - current_size) % 65536))
        writer.close()
        self._make_message_and_send("任务初始化结束", False)

    def _create_download_mission(self, region_list):
        for each_region in region_list:
            download_thread = DownloadThread(self._mission_uuid, self._mission_info, each_region,
                                             self._request_pool, self._download_thread_message, self._thread_message)
            download_thread.start()
            self._free_worker_count -= 1

    def _listen_download_message(self):
        while self._free_worker_count != self._mission_info["thread_num"]:
            message = self._download_thread_message.get()
            self._free_worker_count += 1
            if message["state_code"] == 1:
                if len(message["current_region"]) == 1:
                    self._send_download_mission_finish()
            elif message["state_code"] == 0:
                self._create_download_mission([message["current_region"]])
            elif message["state_code"] == -1:
                if len(message["current_region"]) == 2:
                    tmp_region_list = [message["current_region"]]
                    distribute_list = RegionMaker().get_download_region(tmp_region_list, self._free_worker_count)
                    self._send_download_mission_split(message["current_region"], distribute_list)
                    self._create_download_mission(distribute_list)
                else:
                    self._create_download_mission([[0]])

    def _rename_final_save_file(self):
        self._make_message_and_send("文件整合中", False)
        file_info = self._download_info["file_info"]
        save_file = os.path.join(self._mission_info["save_path"], file_info["filename"])
        os.rename(self._download_info["tmp_path"], save_file)

    def _analyse_target_file_info(self):
        tmp_headers = self._mission_info["headers"].copy()
        tmp_headers["Range"] = "bytes=0-0"
        for try_time in range(3):
            stream_response = self._get_simple_response(self._mission_info["download_link"], tmp_headers)
            if self._check_response_can_access(stream_response):
                headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
                current_url = stream_response.geturl()
                stream_response.close()
                file_info = HTTPHelper.get_download_file_requirement(headers, current_url)
                if file_info["range"] or try_time == 2:
                    return file_info
        return None

    def _generate_file_all_region(self, file_info):
        if file_info and file_info["range"]:
            unassigned_region_list = [[0, file_info["filesize"] - 1]]
            return RegionMaker().get_download_region(unassigned_region_list, self._mission_info["thread_num"])
        else:
            return [[0]]

    def _generate_tmp_file_path(self, file_info):
        if file_info:
            file_name = "{}.tmp".format(file_info["filename"])
            return os.path.join(self._mission_info["save_path"], file_name)
        else:
            return None

    @staticmethod
    def _check_response_can_access(stream_response):
        if stream_response is None:
            return False
        if stream_response.status in [200, 206]:
            return True
        else:
            stream_response.close()
            return False

    def _get_simple_response(self, target_url, headers):
        try:
            return self._request_pool.request("GET", target_url, headers=headers, preload_content=False)
        except UnicodeEncodeError as e:
            self._make_message_and_send(str(e) + target_url, True)
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def _send_download_mission_split(self, current_region, update_region):
        message_dict = dict()
        message_dict["action"] = "write"
        detail_info = {"type": "split", "current_region": current_region, "update_region": update_region}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)

    def _send_download_mission_register(self):
        message_dict = dict()
        message_dict["action"] = "write"
        detail_info = {"type": "register", "lock": self._mission_lock}
        detail_info.update({"mission_info": self._mission_info, "download_info": self._download_info})
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)

    def _send_download_mission_finish(self):
        message_dict = dict()
        message_dict["action"] = "write"
        detail_info = {"type": "finish"}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "HTTPDownloader", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)


class DownloadThread(threading.Thread):
    def __init__(self, mission_uuid, mission_info: dict, current_region: list, request_pool,
                 parent_message: queue.Queue, thread_message: queue.Queue):
        super().__init__()
        self._mission_uuid = mission_uuid
        self._mission_info = mission_info
        self._current_region = current_region.copy()
        self._expect_size = None
        self._request_pool = request_pool
        self._download_step_size = 64 << 10

        self._parent_message = parent_message
        self._thread_message = thread_message

    def run(self) -> None:
        request_headers = self._generate_request_headers()
        stream_response = self._get_simple_response(request_headers)
        if stream_response is None:
            self._send_mission_finish_message(0, 0)
        elif stream_response.status in [200, 206]:
            result = self._request_final_content(stream_response)
            self._send_mission_finish_message(result["state_code"], result["content_length"])
        else:
            self._send_mission_finish_message(0, 0)

    def _generate_request_headers(self):
        base_headers = self._mission_info["headers"].copy()
        base_headers["Range"] = self._make_download_range_headers()
        return base_headers

    def _make_download_range_headers(self):
        if len(self._current_region) == 2:
            self._expect_size = self._current_region[1] - self._current_region[0] + 1
            return "bytes={}-{}".format(self._current_region[0], self._current_region[1])
        else:
            return "bytes={}-".format(self._current_region[0])

    def _get_simple_response(self, headers):
        try:
            target_url = self._mission_info["download_link"]
            response = self._request_pool.request("GET", target_url, headers=headers, preload_content=False)
            return response if self._check_response_region_correct(response) else None
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def _check_response_region_correct(self, response):
        if len(self._current_region) == 2:
            if response is not None:
                expect_range = "bytes {}-{}".format(self._current_region[0], self._current_region[1])
                content_range = response.headers.get("content-range")
                return expect_range in content_range if content_range else False
            else:
                return False
        else:
            return True

    def _request_final_content(self, stream_response: urllib3.response.HTTPResponse):
        content_length = 0
        try:
            for cache in stream_response.stream(self._download_step_size, True):
                cache_length = len(cache)
                if self._expect_size is None or content_length + cache_length <= self._expect_size:
                    self._send_write_content_message(content_length, cache)
                    content_length += cache_length
            stream_response.close()
            return {"state_code": 1, "content_length": content_length}
        except Exception as e:
            self._make_message_and_send(str(e), True)
            stream_response.close()
            return {"state_code": -1, "content_length": content_length}

    def _send_mission_finish_message(self, state_code, content_length):
        """
        :param state_code:
            -1: download time out
             0: download failed
             1: download success
        :param content_length: int
        :return: None
        """
        self._current_region[0] += content_length
        result_dict = {"state_code": state_code, "current_region": self._current_region}
        self._parent_message.put(result_dict)

    def _send_write_content_message(self, current_position, content):
        current_region = self._current_region.copy()
        current_region[0] += current_position
        message_dict = dict()
        message_dict["action"] = "write"
        detail_info = {"type": "write", "current_region": current_region, "content": content}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)

    def _make_message_and_send(self, content, exception: bool):
        message_dict = dict()
        message_dict["action"] = "print"
        detail_info = {"sender": "HTTPDownloader.DownloadThread", "content": content, "exception": exception}
        message_dict["value"] = {"mission_uuid": self._mission_uuid, "detail": detail_info}
        self._thread_message.put(message_dict)
