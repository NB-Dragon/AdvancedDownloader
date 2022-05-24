#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
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

    def _apply_forward_message(self, response_message):
        self._switch_message.put(response_message)

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
            network_info_tool = self._network_tool["info"]
            return network_info_tool.get_resource_simple_info(target_link, result_from_tool["client"])
        else:
            self._send_universal_log(mission_uuid, "file", result_from_tool["error"])
            return None

    def _generate_final_download_info(self, mission_uuid, mission_info, resource_info):
        if resource_info:
            network_info_tool = self._network_tool["info"]
            file_info = network_info_tool.get_download_file_info(mission_uuid, mission_info, resource_info)
            section_info = network_info_tool.get_download_section_info(mission_uuid, mission_info, resource_info)
            return {"total_size": 0, "file_info": file_info, "section_info": section_info}
        else:
            return None

    @staticmethod
    def _calculate_total_size(download_info):
        if isinstance(download_info, dict):
            for value in download_info["section_info"].values():
                download_info["total_size"] += value["section_size"] if value["section_size"] else 0

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_signal_template("thread-log")
        message_detail = {"sender": "ResourceTool", "content": content}
        message_dict["value"] = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        self._apply_forward_message(message_dict)

    @staticmethod
    def _generate_signal_template(receiver):
        return {"handle": "resend", "receiver": receiver, "content": {}}

    @staticmethod
    def _generate_execute_detail(mission_uuid, message_type, message_detail) -> dict:
        signal_detail = {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
        return {"signal_type": "execute", "signal_detail": signal_detail}
