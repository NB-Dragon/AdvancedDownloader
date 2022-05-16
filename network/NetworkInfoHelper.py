#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 09:00
# Create User: NB-Dragon
import os
import re
import urllib.parse
import uuid
import urllib3
from core.util.HTTPContentDisposition import HTTPContentDisposition
from core.util.HTTPContentLength import HTTPContentLength


class NetworkInfoHelper(object):
    def __init__(self):
        self._init_analyze_tool()

    def get_resource_simple_info(self, target_link, connect_client):
        simple_info = None
        if isinstance(connect_client, urllib3.response.HTTPResponse):
            analyze_tool = self._analyze_tool["http(s)"]
            headers = {key.lower(): value for key, value in dict(connect_client.headers).items()}
            simple_info = analyze_tool.get_simple_info(headers, target_link)
        if isinstance(simple_info, dict):
            simple_info["file_name"] = self._parse_unquote_value(simple_info["file_name"])
        return simple_info

    def get_download_file_info(self, mission_uuid, mission_info, resource_info):
        schema_name = self._get_link_schema(mission_info["target_link"])
        mission_save_path = mission_info["save_path"]
        if schema_name in ["http", "https"]:
            analyze_tool = self._analyze_tool["http(s)"]
            return analyze_tool.generate_download_file_info(mission_uuid, mission_save_path, resource_info)
        else:
            return None

    def get_download_section_info(self, mission_uuid, mission_info, resource_info):
        schema_name = self._get_link_schema(mission_info["target_link"])
        if schema_name in ["http", "https"]:
            analyze_tool = self._analyze_tool["http(s)"]
            return analyze_tool.generate_download_section_info(mission_uuid, resource_info)
        else:
            return None

    def _init_analyze_tool(self):
        self._analyze_tool = dict()
        self._analyze_tool["http(s)"] = HTTPAnalyzeTool()

    @staticmethod
    def _get_link_schema(target_link):
        link_parse_result = urllib.parse.urlparse(target_link)
        return link_parse_result.scheme

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

    def generate_download_file_info(self, mission_uuid, mission_save_path, resource_info):
        file_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "file-1"))
        file_size = resource_info["file_size"]
        save_path = self._generate_not_exists_file_name(mission_save_path, resource_info["file_name"])
        section_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "section-1"))
        section_detail = {section_uuid: [0, 0, resource_info["file_size"]]}
        file_detail = {"file_size": file_size, "save_path": save_path, "section_detail": section_detail}
        return {file_uuid: file_detail}

    @staticmethod
    def generate_download_section_info(mission_uuid, resource_info):
        section_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "section-1"))
        section_size = resource_info["file_size"]
        current_progress = [[0, resource_info["file_size"] - 1]] if resource_info["accept_range"] else [[0]]
        section_detail = {"section_hash": None, "section_size": section_size, "current_progress": current_progress}
        return {section_uuid: section_detail}

    @staticmethod
    def _generate_not_exists_file_name(mission_save_path, target_file_name):
        root_path, index = mission_save_path, 0
        name, postfix = os.path.splitext(target_file_name)
        while os.path.exists(os.path.join(root_path, target_file_name)):
            index += 1
            target_file_name = "{}-{}{}".format(name, index, postfix)
        return target_file_name

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
