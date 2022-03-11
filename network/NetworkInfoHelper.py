#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 09:00
# Create User: NB-Dragon
import re
import urllib.parse
import urllib3
from core.util.HTTPContentDisposition import HTTPContentDisposition
from core.util.HTTPContentLength import HTTPContentLength


class NetworkInfoHelper(object):
    def __init__(self):
        self._init_analyze_tool()

    def get_resource_simple_info(self, connect_client, target_link):
        simple_info = None
        if isinstance(connect_client, urllib3.response.HTTPResponse):
            analyze_tool = self._analyze_tool["http(s)"]
            headers = {key.lower(): value for key, value in dict(connect_client.headers).items()}
            simple_info = analyze_tool.get_simple_info(headers, target_link)
        if isinstance(simple_info, dict):
            simple_info["file_name"] = self._parse_unquote_value(simple_info["file_name"])
        return simple_info

    def _init_analyze_tool(self):
        self._analyze_tool = dict()
        self._analyze_tool["http(s)"] = HTTPAnalyzeTool()

    @staticmethod
    def _parse_unquote_value(content):
        while re.findall("%[0-9a-fA-F]{2}", content):
            content = urllib.parse.unquote(content)
        return content


class HTTPAnalyzeTool(object):
    def __init__(self):
        self._content_position = HTTPContentDisposition()
        self._content_length = HTTPContentLength()

    def get_simple_info(self, headers: dict, target_link: str):
        file_name = self._get_download_file_name(headers, target_link)
        file_size = self._get_download_file_size(headers)
        accept_range = self._get_download_accept_range(headers, file_size)
        return {"file_name": file_name, "file_size": file_size, "accept_range": accept_range}

    def _get_download_file_name(self, headers, target_link):
        header_content_disposition = headers.get("content-disposition")
        if isinstance(header_content_disposition, str) and len(header_content_disposition):
            analyze_result = self._content_position.get_disposition_result(header_content_disposition)
            file_name = analyze_result["param"]["filename"] if "filename" in analyze_result["param"] else ""
        else:
            target_link_parse = urllib.parse.urlparse(target_link)
            file_name = target_link_parse.path.split("/")[-1]
        return file_name if len(file_name) else "unknown"

    def _get_download_file_size(self, headers):
        header_content_length = headers.get("content-length")
        header_content_range = headers.get("content-range")
        return self._content_length.get_length_result(header_content_length, header_content_range)

    @staticmethod
    def _get_download_accept_range(headers, file_size):
        header_list = ["content-range", "accept-ranges"]
        range_header_count = len([item for item in header_list if item in headers]) > 0
        return isinstance(file_size, int) and range_header_count
