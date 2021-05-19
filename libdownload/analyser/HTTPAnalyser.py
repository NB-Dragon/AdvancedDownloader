#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import os
import queue
from libdownload.decoder.HTTPHeaderAnalyser import HTTPHeaderAnalyser
from libdownload.other.SectionMaker import SectionMaker
from tools.RuntimeOperator import RuntimeOperator


class HTTPAnalyser(object):
    def __init__(self, schema_name, parent_queue: queue.Queue, runtime_operator: RuntimeOperator):
        self._schema_name = schema_name
        self._parent_queue = parent_queue
        self._runtime_operator = runtime_operator
        self._http_header_analyser = HTTPHeaderAnalyser(runtime_operator)
        self._section_maker = SectionMaker()

    def get_download_info(self, mission_uuid, mission_info):
        self._send_print_message(mission_uuid, "资源连接中", False)
        download_info = self._analyse_target_file_info(mission_uuid, mission_info)
        self._send_print_message(mission_uuid, "资源解析完成", False)
        return download_info

    def _analyse_target_file_info(self, mission_uuid, mission_info):
        tmp_headers = mission_info["headers"].copy() if mission_info["headers"] else dict()
        tmp_headers["Range"] = "bytes=0-0"
        download_link = mission_info["download_link"]
        request_manager = self._http_header_analyser.get_request_manager(self._schema_name, 1, mission_info["proxy"])
        stream_response = self._get_simple_response(request_manager, mission_uuid, download_link, tmp_headers)
        if self._check_response_can_access(stream_response):
            headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
            current_url = stream_response.geturl() or mission_info["download_link"]
            stream_response.close()
            return self._generate_download_info(mission_info, headers, current_url)
        else:
            return None

    def _get_simple_response(self, request_manager, mission_uuid, target_url, headers):
        try:
            return request_manager.request("GET", target_url, headers=headers, preload_content=False)
        except UnicodeEncodeError:
            reason = {"error": "The server does not follow the http standard.", "target": target_url}
            self._send_print_message(mission_uuid, reason, True)
            return None
        except Exception as e:
            self._send_print_message(mission_uuid, str(e), True)
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

    def _generate_download_info(self, mission_info, headers, current_url):
        download_info = dict()
        thread_num, save_path = mission_info["thread_num"], mission_info["save_path"]
        download_info["file_info"] = self._http_header_analyser.get_http_file_info(headers, current_url)
        download_info["all_region"] = self._generate_file_all_region(download_info["file_info"], thread_num)
        download_info["full_path"] = self._generate_file_full_path(download_info["file_info"], save_path)
        return download_info

    def _generate_file_all_region(self, file_info, thread_num):
        if file_info and file_info["range"]:
            unassigned_region_list = [[0, file_info["filesize"] - 1]]
            return self._section_maker.get_download_section(unassigned_region_list, thread_num)
        else:
            return [[0]]

    @staticmethod
    def _generate_file_full_path(file_info, save_path):
        return os.path.join(save_path, file_info["filename"])

    def _send_print_message(self, mission_uuid, content, exception: bool):
        message_dict = {"action": "print", "value": {"mission_uuid": mission_uuid, "detail": None}}
        message_dict["value"]["detail"] = {"sender": "HTTPAnalyser", "content": content, "exception": exception}
        self._send_message_to_listener(message_dict)

    def _send_message_to_listener(self, detail: dict):
        message_dict = {"action": "signal", "receiver": "message", "value": detail}
        self._parent_queue.put(message_dict)
