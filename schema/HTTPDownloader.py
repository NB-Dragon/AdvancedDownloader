#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create Time: 2020/2/21 09:27
# Create User: hya-machine
import re
import os
import queue
import shutil
import threading
import requests
from tool.SpeedListener import SpeedListener
from tool.CurlHelper import CurlHelper


class DownloadThread(threading.Thread):
    def __init__(self, download_link, download_path, mission_info, headers: dict, cookies: dict,
                 message_receiver: queue.Queue, download_thread_communicate: queue.Queue):
        super().__init__()
        self._download_link = download_link
        self._download_path = download_path
        self._mission_info = mission_info
        self._message_receiver = message_receiver
        self._download_thread_communicate = download_thread_communicate
        self._headers = headers.copy()
        self._cookies = cookies.copy()
        self._download_step_size = 2 ** 16

    """
    message [queue_index, state_code]
    state_code=1 : download success
    state_code=0 : download failed
    state_code=-1: download time out
    state_code=-2: download forbidden
    """

    def run(self) -> None:
        mission_index = self._mission_info["index"]
        self._headers['Range'] = self._make_download_range_headers()
        if self._headers['Range']:
            stream_response = self._make_response(self._headers, self._cookies)
            if stream_response is None:
                self._download_thread_communicate.put({"index": mission_index, "state_code": 0})
            elif stream_response.status_code in [200, 206]:
                result_code = self._write_file_from_stream(stream_response)
                self._download_thread_communicate.put({"index": mission_index, "state_code": result_code})
            elif stream_response.status_code == 416:
                self._download_thread_communicate.put({"index": mission_index, "state_code": 1})
            else:
                self._download_thread_communicate.put({"index": mission_index, "state_code": 0})
        else:
            self._download_thread_communicate.put({"index": mission_index, "state_code": 1})

    def _write_file_from_stream(self, stream_response):
        current_size = self._mission_info["correct_size"]
        writer = self._get_writer_after_seek_and_truncate(self._mission_info["filename"], current_size)
        try:
            for content in stream_response.iter_content(self._download_step_size):
                writer.write(content)
                writer.flush()
            result_code = 1
        except Exception as e:
            self._make_message_and_send(str(e), True)
            result_code = -1
        finally:
            writer.close()
            stream_response.close()
        return result_code

    def _make_download_range_headers(self):
        start = self._mission_info["start"] + self._mission_info["correct_size"]
        if self._mission_info["end"] == 0:
            return "bytes={}-".format(start)
        elif start <= self._mission_info["end"]:
            return "bytes={}-{}".format(start, self._mission_info["end"])
        else:
            return None

    def _make_response(self, headers, cookies):
        try:
            response = requests.get(self._download_link, stream=True, headers=headers, cookies=cookies, timeout=10)
            return response if self._check_response_region_correct(response) else None
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def _check_response_region_correct(self, response):
        region = response.headers.get("content-range")
        if region is not None:
            request_region = str(self._headers["Range"]).replace("=", " ")
            if request_region.endswith("-"):
                return re.findall("{}\\d+/\\d+".format(request_region), region)
            else:
                return re.findall("{}/\\d+".format(request_region), region)
        elif self._mission_info["start"] == 0 and self._mission_info["end"] == 0:
            return True
        else:
            return False

    def _make_message_and_send(self, content, exception: bool):
        message = {"sender": "DownloadThread", "title": self._mission_info, "content": content}
        self._message_receiver.put({"message": message, "exception": exception})

    @staticmethod
    def _get_writer_after_seek_and_truncate(file_name, position):
        if position == 0:
            os.remove(file_name)
            return open(file_name, 'a+b')
        else:
            writer = open(file_name, 'a+b')
            writer.seek(position)
            writer.truncate()
            return writer


class HTTPDownloader(object):
    def __init__(self, message_receiver, download_link, work_directory, download_index,
                 headers: dict = None, cookies: dict = None):
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._message_receiver = message_receiver
        self._download_link = download_link

        self._speed_listener = SpeedListener(message_receiver)
        self._curl_helper = CurlHelper(download_link, message_receiver, headers, cookies)
        self._work_directory = work_directory
        self._max_thread_count = 128  # 每个任务最多同时128个线程下载

        self._target_file_info = None
        self._download_index = download_index
        self._download_path = ""
        self._download_part_file_name = []
        self._download_queue = {}
        self._download_thread_communicate = queue.Queue()

    def start_download_mission(self):
        final_download_link = self._curl_helper.get_final_location()
        if final_download_link:
            self._target_file_info = self._analyse_link_info(final_download_link)
            if self._check_can_download():
                self._download_path = self._get_download_directory()
                self._init_download_directory()
                self._init_download_part_file()
                self._make_download_queue()
                self._start_speed_listener()
                self._create_download_mission()
                self._listen_download_message()
                self._speed_listener.send_stop_state()
                self._splice_all_part_file()
            else:
                self._make_message_and_send("资源禁止访问，请确认验证信息", False)
        else:
            self._make_message_and_send("资源连接失败，请检查网络连接", False)

    def _analyse_link_info(self, final_download_link):
        temp_agent = self._headers.copy()
        temp_agent["Range"] = "bytes=0-1"
        for try_time in range(3):
            stream_response = self._make_response(final_download_link, temp_agent, self._cookies)
            if self._check_response_can_access(stream_response):
                headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
                stream_response.close()
                file_name = self._get_download_file_name(headers, final_download_link)
                accept_ranges = self._judge_can_range_file(headers)
                content_length = self._get_download_file_size(headers)
                range_download = accept_ranges and content_length is not None
                if range_download:
                    return {"file-name": file_name, "range-download": range_download, "content-length": content_length}
                elif try_time == 2:
                    return {"file-name": file_name, "range-download": range_download, "content-length": content_length}
        return None

    @staticmethod
    def _get_download_file_name(headers, link):
        content_disposition = headers.get("content-disposition")
        if content_disposition and "filename=" in content_disposition:
            content_list = content_disposition.split(";")
            content_list = [content.strip() for content in content_list[:]]
            filename_content = [content for content in content_list if content.startswith("filename=")][0]
            filename = re.findall("(?<=filename=).*", filename_content)[0]
            if re.findall("^[\"].*?[\"]$", filename):
                filename = eval(filename)
        else:
            filename = os.path.split(link)[-1].split("?")[0]
        return filename

    @staticmethod
    def _judge_can_range_file(headers):
        return "content-range" in headers or "accept-ranges" in headers

    @staticmethod
    def _get_download_file_size(headers):
        if "content-range" in headers:
            return int(re.findall("bytes \\d+-\\d+/(\\d+)", headers["content-range"])[0])
        elif "content-length" in headers:
            return int(headers.get("content-length"))
        else:
            return None

    def _check_can_download(self):
        if self._target_file_info is not None:
            return self._target_file_info["file-name"] != ""
        else:
            return False

    def _get_download_directory(self):
        file_name_no_postfix = os.path.splitext(self._target_file_info["file-name"])[0]
        return os.path.join(self._work_directory, file_name_no_postfix)

    def _init_download_directory(self):
        if not os.path.exists(self._download_path):
            os.mkdir(self._download_path)

    def _init_download_part_file(self):
        file_name = self._target_file_info["file-name"]
        if self._target_file_info["range-download"]:
            mission_content_size = self._target_file_info["content-length"]
            if mission_content_size >= self._max_thread_count:
                for index in range(1, self._max_thread_count + 1):
                    self._download_part_file_name.append(self._create_part_file_with_index(file_name, index))
            else:
                self._download_part_file_name.append(self._create_part_file_with_index(file_name, 1))
        else:
            self._download_part_file_name.append(self._create_part_file_with_index(file_name, 1))

    def _create_part_file_with_index(self, filename, part_index):
        file_name = "{}.part{}".format(filename, part_index)
        absolute_file_path = os.path.join(self._download_path, file_name)
        open(absolute_file_path, 'a+b').close()
        return absolute_file_path

    @staticmethod
    def _make_each_thread_size(content_size, thread_count):
        low_base_size = content_size // thread_count
        content_size_list = [low_base_size] * thread_count
        height_size_count = content_size - low_base_size * thread_count
        content_size_list[0:height_size_count] = [low_base_size + 1] * height_size_count
        return content_size_list

    def _make_download_queue(self):
        if len(self._download_part_file_name) > 1:
            current_sum_size = 0
            mission_content_size = self._target_file_info["content-length"]
            each_thread_size = self._make_each_thread_size(mission_content_size, self._max_thread_count)
            for index in range(1, self._max_thread_count + 1):
                file_name = self._download_part_file_name[index - 1]
                start_position = current_sum_size
                end_position = current_sum_size + each_thread_size[index - 1] - 1
                current_sum_size += each_thread_size[index - 1]
                mission_config = self._make_each_mission_config(index, file_name, start_position, end_position)
                self._download_queue[str(index)] = mission_config
        else:
            self._make_one_thread_mission()

    def _make_one_thread_mission(self):
        self._download_queue.clear()
        file_name = self._download_part_file_name[0]
        mission_config = self._make_each_mission_config(1, file_name, 0, 0)
        self._download_queue["1"] = mission_config
        self._update_mission_correct_size("1")

    def _update_mission_correct_size(self, queue_key):
        if self._target_file_info["range-download"]:
            mission = self._download_queue[queue_key]
            mission_name = mission["filename"]
            mission["correct_size"] = os.path.getsize(mission_name)

    @staticmethod
    def _make_each_mission_config(index, file_name, start, end):
        mission_template = {"index": index, "filename": file_name, "start": start, "end": end}
        file_size = os.path.getsize(file_name)
        mission_template["correct_size"] = file_size
        return mission_template

    def _start_speed_listener(self):
        self._speed_listener.set_download_index(self._download_index)
        self._speed_listener.set_download_mode(self._target_file_info["range-download"])
        self._speed_listener.set_listen_file_list(self._download_part_file_name)
        self._speed_listener.start()

    def _splice_all_part_file(self):
        final_save_name = os.path.join(self._work_directory, self._target_file_info["file-name"])
        file_writer = open(final_save_name, 'w+b')
        for each_part_file_name in self._download_part_file_name:
            part_file_reader = open(each_part_file_name, 'rb')
            file_writer.write(part_file_reader.read())
            part_file_reader.close()
            os.remove(each_part_file_name)
        file_writer.close()
        shutil.rmtree(self._download_path)

    def _create_download_mission(self):
        for each_mission_key in self._download_queue.keys():
            self._start_thread_by_identity(each_mission_key)

    def _listen_download_message(self):
        while len(self._download_queue) != 0:
            if not self._download_thread_communicate.empty():
                message = self._download_thread_communicate.get()
                download_queue_key = str(message["index"])
                if message["state_code"] == 1:
                    if self._check_file_in_normal_region(download_queue_key):
                        self._download_queue.pop(download_queue_key)
                    else:
                        self._start_thread_by_identity(download_queue_key)
                elif message["state_code"] == 0:
                    self._start_thread_by_identity(download_queue_key)
                elif message["state_code"] == -1:
                    self._update_mission_correct_size(download_queue_key)
                    self._start_thread_by_identity(download_queue_key)

    def _check_file_in_normal_region(self, index):
        each_download_queue = self._download_queue[index]
        if each_download_queue["end"] != 0:
            current_size = os.path.getsize(each_download_queue["filename"])
            expect_size = each_download_queue["end"] - each_download_queue["start"] + 1
            if current_size > expect_size:
                os.remove(each_download_queue["filename"])
            return current_size == expect_size
        else:
            return True

    def _start_thread_by_identity(self, thread_id: str):
        mission_info = self._download_queue[thread_id]
        new_thread = DownloadThread(self._download_link, self._download_path, mission_info,
                                    self._headers, self._cookies,
                                    self._message_receiver, self._download_thread_communicate)
        new_thread.start()

    @staticmethod
    def _check_response_can_access(stream_response):
        if stream_response is None:
            return False
        if stream_response.status_code in [200, 206]:
            return True
        else:
            stream_response.close()
            return False

    def _make_response(self, download_link, headers, cookies):
        try:
            return requests.get(download_link, stream=True, timeout=10, headers=headers, cookies=cookies)
        except Exception as e:
            self._make_message_and_send(str(e), True)
            return None

    def _make_message_and_send(self, content, exception: bool):
        message = {"sender": "HTTPHelper", "title": self._download_index, "content": content}
        self._message_receiver.put({"message": message, "exception": exception})
