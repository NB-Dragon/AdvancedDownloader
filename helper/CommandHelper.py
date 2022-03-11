#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/03/01 20:00
# Create User: NB-Dragon
import uuid
import urllib.parse
from helper.ArgumentReader import ArgumentReader
from helper.BashReader import BashReader
from helper.ParserHelper import ParserHelper


class CommandHelper(object):
    def __init__(self, project_helper):
        self._bash_reader = BashReader()
        self._argument_reader = ArgumentReader()
        self._parse_helper = ParserHelper(project_helper.get_project_version())
        self._param_error_tips = "The current parameters are incomplete, please read the document."

    def get_next_command_message(self):
        command_content = self._bash_reader.get_next_line()
        command_arg = self._argument_reader.parse_argument(command_content)
        if len(command_arg) >= 1:
            command_type = command_arg.pop(0)
            if command_type == "create":
                return self._generate_create_message(command_arg)
            elif command_type == "start":
                return self._generate_start_message(command_arg)
            elif command_type == "pause":
                return self._generate_pause_message(command_arg)
            elif command_type == "delete":
                return self._generate_delete_message(command_arg)
            elif command_type == "exit":
                return None
            else:
                return self._generate_unknown_message(command_type)
        else:
            return {"success": False, "message": None}

    def _generate_create_message(self, command_arg: list):
        parser_args = self._parse_helper.get_runtime_arguments(command_arg)
        if parser_args:
            mission_detail = self._generate_mission_detail(parser_args)
            mission_uuid, message_detail = mission_detail["mission_uuid"], mission_detail["detail"]
            response_message = self._send_semantic_transform(mission_uuid, "create_command", message_detail)
            return {"success": True, "message": response_message}
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
            return {"success": True, "message": response_message}

    def _generate_start_message(self, command_arg: list):
        if len(command_arg) >= 1:
            mission_uuid = command_arg[0]
            response_message = self._send_semantic_transform(mission_uuid, "start_command", None)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_pause_message(self, command_arg: list):
        if len(command_arg) >= 1:
            mission_uuid = command_arg[0]
            response_message = self._send_semantic_transform(mission_uuid, "pause_command", None)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_delete_message(self, command_arg: list):
        if len(command_arg) >= 2:
            mission_uuid, delete_file = command_arg[0], command_arg[1]
            response_detail = {"delete_file": True if delete_file == "1" else False}
            response_message = self._send_semantic_transform(mission_uuid, "delete_command", response_detail)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_unknown_message(self, command_type):
        exception_tips = "Unknown command type: {}".format(command_type)
        response_message = self._send_universal_log(None, "console", exception_tips)
        return {"success": True, "message": response_message}

    def _generate_mission_detail(self, input_args):
        mission_uuid = str(uuid.uuid1())
        mission_info = self._get_default_mission_info(input_args)
        response_detail = {"mission_info": mission_info}
        return {"mission_uuid": mission_uuid, "detail": response_detail}

    def _get_default_mission_info(self, mission_parameter):
        standard_mission_info = dict()
        target_link = self._get_url_after_quote(mission_parameter.url)
        standard_mission_info["target_link"] = target_link
        standard_mission_info["save_path"] = mission_parameter.output
        standard_mission_info["thread_count"] = mission_parameter.thread
        standard_mission_info["headers"] = mission_parameter.headers
        standard_mission_info["proxy"] = mission_parameter.proxy
        return standard_mission_info

    @staticmethod
    def _get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/?#[]@!$&'()*+,;=%")

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_action_signal_template("thread-log")
        message_detail = {"sender": "CommandHelper", "content": content}
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        return message_dict

    def _send_semantic_transform(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_action_signal_template("thread-transform")
        message_dict["value"] = self._generate_signal_value(mission_uuid, message_type, message_detail)
        return message_dict

    @staticmethod
    def _generate_action_signal_template(receiver):
        return {"receiver": receiver, "value": {}}

    @staticmethod
    def _generate_signal_value(mission_uuid, message_type, message_detail) -> dict:
        return {"mission_uuid": mission_uuid, "message_type": message_type, "detail": message_detail}
