#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 09:00
# Create User: NB-Dragon
import urllib.parse
from network.NetworkRequestHelper import NetworkRequestHelper


class NetworkDetectHelper(object):
    def __init__(self, ca_cert_path, global_config):
        self._ca_cert_path = ca_cert_path
        self._global_config = global_config
        self._init_detect_tool()

    def get_resource_simple_request(self, target_link, headers, proxy):
        schema_name = self._get_link_schema(target_link)
        if schema_name in ["http", "https"]:
            tmp_headers = headers.copy() if headers else dict()
            tmp_headers["Range"] = "bytes=0-0"
            request_manager = self._network_request_helper.get_request_manager(target_link, 1, proxy)
            return self._network_request_helper.get_connect_client(request_manager, target_link, tmp_headers)
        else:
            return {"client": None, "error": "Unknown request schema {}".format(schema_name)}

    def _init_detect_tool(self):
        self._network_request_helper = NetworkRequestHelper(self._ca_cert_path, self._global_config["timeout"])

    @staticmethod
    def _get_link_schema(target_link):
        link_parse_result = urllib.parse.urlparse(target_link)
        return link_parse_result.scheme
