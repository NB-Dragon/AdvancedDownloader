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
from Class.SpeedListener import SpeedListener


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
            elif stream_response.status_code == 403:
                self._download_thread_communicate.put({"index": mission_index, "state_code": -2})
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
            self._make_message_and_send(str(e))
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
            self._make_message_and_send(str(e))
            return None

    def _check_response_region_correct(self, response):
        region = response.headers.get("content-range")
        if region is not None:
            request_region = str(self._headers["Range"]).replace("=", " ")
            if request_region.endswith("-"):
                return re.findall("{}\\d+/\\d+".format(request_region), region)
            else:
                return re.findall("{}/\\d+".format(request_region), region)
        else:
            return False

    def _make_message_and_send(self, content):
        message = {"sender": "DownloadThread", "title": self._mission_info, "result": content}
        self._message_receiver.put(message)

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
    def __init__(self, message_receiver, download_link, work_directory, headers: dict = None, cookies: dict = None):
        self._headers = headers if headers is not None else {}
        self._cookies = cookies if cookies is not None else {}
        self._message_receiver = message_receiver
        self._download_link = download_link
        self._work_directory = work_directory

        self._download_link_info = self._analyse_link_info()
        self._max_thread_count = 128  # 每个任务最多同时128个线程下载

        self._download_path = ""
        self._download_part_file_name = []
        self._download_queue = {}
        self._download_thread_communicate = queue.Queue()
        self._speed_listener = None

    def start_download_mission(self):
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
            self._make_message_and_send("资源禁止访问，请确认验证信息")

    def _check_can_download(self):
        if self._download_link_info is not None:
            return self._download_link_info["file-name"] != ""
        else:
            return False

    def _make_download_queue(self):
        if len(self._download_part_file_name) > 1:
            current_sum_size = 0
            mission_content_size = self._download_link_info['content-length']
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
        file_name = self._make_file_name_for_each_part(1)
        self._download_queue["1"] = self._make_each_mission_config(1, file_name, 0, 0)

    def _start_speed_listener(self):
        file_name = self._download_link_info['file-name']
        self._speed_listener = SpeedListener(file_name, self._download_part_file_name, self._message_receiver)
        self._speed_listener.start()

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
                    self._update_file_correct_size(download_queue_key)
                    self._start_thread_by_identity(download_queue_key)
                elif message["state_code"] == -2:
                    self._make_message_and_send("资源禁止访问，请确认验证信息")
                    self._speed_listener.send_stop_state()
                    break

    def _update_file_correct_size(self, index):
        each_download_queue = self._download_queue[index]
        file_name = each_download_queue["filename"]
        each_download_queue["correct_size"] = os.path.getsize(file_name)

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

    def _splice_all_part_file(self):
        final_save_name = os.path.join(self._work_directory, self._download_link_info['file-name'])
        file_writer = open(final_save_name, 'w+b')
        for each_part_file_name in self._download_part_file_name:
            part_file_reader = open(each_part_file_name, 'rb')
            file_writer.write(part_file_reader.read())
            part_file_reader.close()
            os.remove(each_part_file_name)
        file_writer.close()
        shutil.rmtree(self._download_path)

    def _start_thread_by_identity(self, thread_id: str):
        mission_info = self._download_queue[thread_id]
        new_thread = DownloadThread(self._download_link, self._download_path, mission_info,
                                    self._headers, self._cookies,
                                    self._message_receiver, self._download_thread_communicate)
        new_thread.start()

    def _init_download_part_file(self):
        if self._download_link_info['range-download']:
            mission_content_size = self._download_link_info['content-length']
            if mission_content_size >= self._max_thread_count:
                for index in range(1, self._max_thread_count + 1):
                    self._download_part_file_name.append(self._make_file_name_for_each_part(index))
            else:
                self._download_part_file_name.append(self._make_file_name_for_each_part(1))
        else:
            self._download_part_file_name.append(self._make_file_name_for_each_part(1))

    @staticmethod
    def _make_each_mission_config(index, file_name, start, end):
        mission_template = {"index": index, "filename": file_name, "start": start, "end": end}
        file_size = os.path.getsize(file_name)
        mission_template["correct_size"] = file_size
        return mission_template

    def _make_file_name_for_each_part(self, part_index):
        file_name = "{}.part{}".format(self._download_link_info['file-name'], part_index)
        absolute_file_path = os.path.join(self._download_path, file_name)
        open(absolute_file_path, 'a+b').close()
        return absolute_file_path

    def _get_download_directory(self):
        file_name_no_postfix = os.path.splitext(self._download_link_info['file-name'])[0]
        return os.path.join(self._work_directory, file_name_no_postfix)

    def _init_download_directory(self):
        if not os.path.exists(self._download_path):
            os.mkdir(self._download_path)

    def _analyse_link_info(self):
        if not self._recursive_update_link():
            return None
        stream_response = self._make_response(self._headers, self._cookies)
        if self._check_response_can_access(stream_response):
            file_name = self._analyse_file_name(stream_response)
            accept_ranges = self._judge_can_range_file() is not None
            content_length = stream_response.headers.get('content-length')
            content_length = int(content_length) if content_length is not None else None
            range_download = content_length is not None and accept_ranges
            stream_response.close()
            return {"file-name": file_name, "content-length": content_length, "range-download": range_download}
        else:
            return None

    @staticmethod
    def _check_response_can_access(stream_response):
        if stream_response is None:
            return False
        if stream_response.status_code not in [200, 206]:
            stream_response.close()
            return False
        else:
            return True

    @staticmethod
    def _analyse_file_name(response):
        content_disposition = response.headers.get('Content-disposition')
        if content_disposition and "filename=" in content_disposition:
            content_list = content_disposition.split(";")
            content_list = [content.strip() for content in content_list[:]]
            filename_content = [content for content in content_list if content.startswith("filename=")][0]
            filename = re.findall("(?<=filename=).*", filename_content)[0]
            if re.findall("^[\"].*?[\"]$", filename):
                filename = eval(filename)
        else:
            filename = os.path.split(response.url)[-1].split("?")[0]
        return filename

    def _judge_can_range_file(self):
        temp_agent = self._headers.copy()
        temp_agent['Range'] = "bytes=0-19"
        stream_response = self._make_response(temp_agent, self._cookies)
        content_range = stream_response.headers.get('content-range')
        accept_range = stream_response.headers.get('accept-ranges')
        stream_response.close()
        return content_range or accept_range

    @staticmethod
    def _make_each_thread_size(content_size, thread_count):
        low_base_size = content_size // thread_count
        content_size_list = [low_base_size] * thread_count
        height_size_count = content_size - low_base_size * thread_count
        content_size_list[0:height_size_count] = [low_base_size + 1] * height_size_count
        return content_size_list

    def _recursive_update_link(self):
        while True:
            stream_response = self._make_response(self._headers, self._cookies)
            if stream_response is None: return False
            temp_link = stream_response.url
            if temp_link == self._download_link:
                stream_response.close()
                return True
            else:
                self._download_link = temp_link
                stream_response.close()

    def _make_response(self, headers, cookies):
        try:
            return requests.get(self._download_link, stream=True, timeout=10, headers=headers, cookies=cookies)
        except Exception as e:
            self._make_message_and_send(str(e))
            return None

    def _make_message_and_send(self, content):
        if not hasattr(self, '_download_link_info') or self._download_link_info is None:
            title = "未知文件名"
        else:
            title = self._download_link_info['file-name']
        message = {"sender": "HTTPHelper", "title": title, "result": content}
        self._message_receiver.put(message)
