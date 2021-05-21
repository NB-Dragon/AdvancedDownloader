#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
from core.decoder.HTTPHeaderAnalyzer import HTTPHeaderAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class HTTPAnalyzer(object):
    def __init__(self, schema_name, main_thread_message: queue.Queue, runtime_operator: RuntimeOperator):
        self._schema_name = schema_name
        self._main_thread_message = main_thread_message
        self._http_header_analyser = HTTPHeaderAnalyzer(runtime_operator)

    def get_download_info(self, mission_uuid, mission_info):
        self._make_message_and_send(mission_uuid, "资源连接中", False)
        download_info = self._analyse_target_file_info(mission_uuid, mission_info)
        self._make_message_and_send(mission_uuid, "资源解析完成", False)
        return download_info

    @staticmethod
    def get_current_finish_size(download_info):
        if download_info["other"]["range"] is False:
            return download_info["other"]["section"][0][0]
        else:
            incomplete_size = sum([x[1] - x[0] + 1 for x in download_info["other"]["section"]])
            return download_info["filesize"] - incomplete_size

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
            self._make_message_and_send(mission_uuid, reason, True)
            return None
        except Exception as e:
            self._make_message_and_send(mission_uuid, str(e), True)
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
        thread_num, save_path = mission_info["thread_num"], mission_info["save_path"]
        return self._http_header_analyser.generate_resource_info(headers, current_url, thread_num)

    def _make_message_and_send(self, mission_uuid, content, exception: bool):
        signal_header = self._generate_action_signal_template("print")
        signal_header["value"] = self._generate_print_value(mission_uuid, content, exception)
        self._main_thread_message.put(signal_header)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"action": "signal", "receiver": receiver, "value": None}

    @staticmethod
    def _generate_print_value(mission_uuid, content, exception: bool):
        message_type = "exception" if exception else "normal"
        message_detail = {"sender": "HTTPAnalyser", "content": content}
        return {"type": message_type, "mission_uuid": mission_uuid, "detail": message_detail}
