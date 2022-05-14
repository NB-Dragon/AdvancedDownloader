#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import os
import uuid
from network.NetworkDetectHelper import NetworkDetectHelper
from network.NetworkInfoHelper import NetworkInfoHelper


class ResourceTool(object):
    def __init__(self, project_helper, switch_message):
        self._project_helper = project_helper
        self._switch_message = switch_message
        self._init_network_tool()

    def get_download_info(self, mission_uuid, mission_info):
        self._send_universal_log(mission_uuid, "console", "Analyzing...")
        resource_info = self._get_resource_simple_request(mission_uuid, mission_info)
        download_info = self._generate_final_download_info(mission_uuid, mission_info, resource_info)
        self._calculate_total_size(download_info)
        self._send_universal_log(mission_uuid, "console", "Analyzing done")
        return download_info

    def _init_network_tool(self):
        self._network_tool = dict()
        static_cert_path = self._project_helper.get_static_cert_path()
        global_config = self._project_helper.get_project_config()["global"]
        self._network_tool["detect"] = NetworkDetectHelper(static_cert_path, global_config["timeout"])
        self._network_tool["info"] = NetworkInfoHelper()

    def _get_resource_simple_request(self, mission_uuid, mission_info):
        target_link, headers, proxy = mission_info["target_link"], mission_info["headers"], mission_info["proxy"]
        result_from_tool = self._network_tool["detect"].get_resource_simple_request(target_link, headers, proxy)
        if result_from_tool["client"] is not None:
            return self._network_tool["info"].get_resource_simple_info(result_from_tool["client"], target_link)
        else:
            self._send_universal_log(mission_uuid, "file", result_from_tool["error"])
            return None

    def _generate_final_download_info(self, mission_uuid, mission_info, resource_info):
        if resource_info:
            file_info = self._generate_file_info_from_resource(mission_uuid, mission_info, resource_info)
            section_info = self._generate_section_info_from_resource(mission_uuid, resource_info)
            return {"total_size": 0, "file_info": file_info, "section_info": section_info}
        else:
            return None

    @staticmethod
    def _calculate_total_size(download_info):
        if isinstance(download_info, dict):
            for value in download_info["section_info"].values():
                download_info["total_size"] += value["section_size"] if value["section_size"] else 0

    def _generate_file_info_from_resource(self, mission_uuid, mission_info, resource_info):
        # Attempt to identify torrent information
        if "accept_range" in resource_info:
            file_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "file-1"))
            file_size = resource_info["file_size"]
            save_path = self._generate_not_exists_file_name(mission_info, resource_info["file_name"])
            section_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "section-1"))
            section_detail = {section_uuid: [0, 0, resource_info["file_size"]]}
            file_detail = {"file_size": file_size, "save_path": save_path, "section_detail": section_detail}
            return {file_uuid: file_detail}
        else:
            return resource_info["file_info"]

    @staticmethod
    def _generate_section_info_from_resource(mission_uuid, resource_info):
        # Attempt to identify torrent information
        if "accept_range" in resource_info:
            section_uuid = str(uuid.uuid3(uuid.UUID(mission_uuid), "section-1"))
            section_size = resource_info["file_size"]
            current_progress = [[0, resource_info["file_size"] - 1]] if resource_info["accept_range"] else [[0]]
            section_detail = {"section_hash": None, "section_size": section_size, "current_progress": current_progress}
            return {section_uuid: section_detail}
        else:
            return resource_info["section_info"]

    @staticmethod
    def _generate_not_exists_file_name(mission_info, file_name):
        root_path, index = mission_info["save_path"], 0
        name, postfix = os.path.splitext(file_name)
        while os.path.exists(os.path.join(root_path, file_name)):
            index += 1
            file_name = "{}-{}{}".format(name, index, postfix)
        return file_name

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "ResourceTool", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        self._switch_message.append_message(message_dict)

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
