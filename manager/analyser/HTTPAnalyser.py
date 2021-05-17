#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import queue
import urllib3
from schema.analyser.HTTPHelper import HTTPHelper
from tools.RuntimeOperator import RuntimeOperator


class HTTPAnalyser(object):
    def __init__(self, runtime_operator: RuntimeOperator, parent_queue: queue.Queue):
        self._runtime_operator = runtime_operator
        self._parent_queue = parent_queue

    def get_download_info(self, schema, mission_info, mission_uuid):
        tmp_headers = mission_info["headers"].copy() if mission_info["headers"] else dict()
        tmp_headers["Range"] = "bytes=0-0"
        download_link = mission_info["download_link"]
        request_manager = self.get_request_manager(schema, mission_info)
        stream_response = self._get_simple_response(request_manager, mission_uuid, download_link, tmp_headers)
        if self._check_response_can_access(stream_response):
            headers = {key.lower(): value for key, value in dict(stream_response.headers).items()}
            current_url = stream_response.geturl() or mission_info["download_link"]
            stream_response.close()
            return HTTPHelper.get_download_file_requirement(headers, current_url)
        else:
            return None

    def get_request_manager(self, schema, mission_info):
        if mission_info["proxy"] is None:
            return self._get_request_pool_manager(mission_info["thread_num"])
        else:
            proxy_url = "{}://{}".format(schema, mission_info["proxy"])
            return self._get_request_proxy_manager(mission_info["thread_num"], proxy_url)

    def _get_request_pool_manager(self, alive_count):
        cert_pem_file = self._runtime_operator.get_static_cert_path()
        return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file, maxsize=alive_count, timeout=15)

    def _get_request_proxy_manager(self, alive_count, proxy_url):
        cert_pem_file = self._runtime_operator.get_static_cert_path()
        return urllib3.ProxyManager(proxy_url=proxy_url,
                                    cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file, maxsize=alive_count, timeout=15)

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

    def _send_print_message(self, mission_uuid, content, exception: bool):
        message_dict = {"action": "print", "value": {"mission_uuid": mission_uuid, "detail": None}}
        message_dict["value"]["detail"] = {"sender": "HTTPAnalyser", "content": content, "exception": exception}
        self._send_message_to_listener(message_dict)

    def _send_message_to_listener(self, detail: dict):
        message_dict = {"action": "signal", "receiver": "message", "detail": detail}
        self._parent_queue.put(message_dict)
