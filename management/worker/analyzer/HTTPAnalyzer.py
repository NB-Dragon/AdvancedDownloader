#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import json
import uuid
from core.decoder.HTTPHeaderAnalyzer import HTTPHeaderAnalyzer
from tools.RuntimeOperator import RuntimeOperator


class HTTPAnalyzer(object):
    def __init__(self, schema_name, worker_message_queue, runtime_operator: RuntimeOperator):
        self._schema_name = schema_name
        self._worker_message_queue = worker_message_queue
        self._http_header_analyzer = HTTPHeaderAnalyzer(runtime_operator)

    def get_download_info(self, mission_uuid, mission_info):
        self._make_message_and_send(mission_uuid, "资源连接中", False)
        mission_info = json.loads(json.dumps(mission_info))
        source_info = self._analyze_target_source_info(mission_uuid, mission_info)
        download_info = self._generate_final_download_info(mission_uuid, source_info)
        self._handle_download_info_summary(download_info)
        self._make_message_and_send(mission_uuid, "资源解析完成", False)
        return download_info

    def _analyze_target_source_info(self, mission_uuid, mission_info):
        tmp_headers = mission_info["headers"] if mission_info["headers"] else dict()
        tmp_headers["Range"] = "bytes=0-0"
        download_link = mission_info["download_link"]
        request_manager = self._http_header_analyzer.get_request_manager(self._schema_name, 1, mission_info["proxy"])
        stream_response = self._get_simple_response(mission_uuid, request_manager, download_link, tmp_headers)
        if self._check_response_can_access(stream_response):
            headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
            current_url = stream_response.geturl() or mission_info["download_link"]
            stream_response.close()
            return self._http_header_analyzer.generate_resource_info(headers, current_url)
        else:
            return None

    def _generate_final_download_info(self, mission_uuid, source_info):
        if source_info:
            file_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "file: 1"))
            file_info = {"save_path": source_info["filename"], "file_size": source_info["filesize"]}
            section_progress = self._generate_section_progress(source_info)
            section_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "section: 1"))
            section_info = {"progress": section_progress, "file_mapping": dict()}
            section_info["file_mapping"][file_uuid] = [0]
            section_info["file_mapping"][file_uuid].extend(section_progress[0])
            return {"total_size": 0, "file_dict": {file_uuid: file_info}, "section_dict": {section_uuid: section_info}}
        else:
            return None

    def _get_simple_response(self, mission_uuid, request_manager, target_url, headers):
        try:
            return request_manager.request("GET", target_url, headers=headers, preload_content=False)
        except UnicodeEncodeError:
            reason = {"error": "The server does not follow the http standard.", "target": target_url}
            self._make_message_and_send(mission_uuid, reason, True)
            return None
        except Exception as e:
            self._make_message_and_send(mission_uuid, str(e), True)
            return None

    def _make_message_and_send(self, mission_uuid, content, exception: bool):
        signal_header = self._generate_action_signal_template("print")
        message_type = "exception" if exception else "normal"
        message_detail = {"sender": "HTTPAnalyzer", "content": content}
        signal_header["value"] = self._generate_signal_value(message_type, mission_uuid, message_detail)
        self._worker_message_queue.put(signal_header)

    @staticmethod
    def _handle_download_info_summary(standard_dict):
        if standard_dict:
            for value in standard_dict["file_dict"].values():
                standard_dict["total_size"] += value["file_size"] if value["file_size"] else 0
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

    @staticmethod
    def _generate_section_progress(source_info):
        return [[0, source_info["filesize"] - 1]] if source_info["range"] else [[0]]

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": None}

    @staticmethod
    def _generate_signal_value(signal_type, mission_uuid, mission_detail):
        return {"type": signal_type, "mission_uuid": mission_uuid, "detail": mission_detail}
