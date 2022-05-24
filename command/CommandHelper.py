#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/03/01 20:00
# Create User: NB-Dragon
import uuid
import urllib.parse
from command.CreateParser import CreateParser
from command.DeleteParser import DeleteParser
from command.UniversalParser import UniversalParser
from core.util.HTTPHeaderGenerator import HTTPHeaderGenerator
from helper.ArgumentReader import ArgumentReader
from helper.BashReader import BashReader


class CommandHelper(object):
    def __init__(self, version_name):
        self._version_name = version_name
        self._bash_reader = BashReader()
        self._argument_reader = ArgumentReader()
        self._param_error_tips = "The current parameters are incomplete. Please read the document."
        self._mode_error_tips = "You need to select the runtime mode. All or detail. Please read the document."
        self._init_module_tool()

    def _init_module_tool(self):
        self._module_tool = dict()
        self._module_tool["create_parser"] = CreateParser()
        self._module_tool["delete_parser"] = DeleteParser()
        self._module_tool["universal_parser"] = UniversalParser()

    def get_next_command_message(self):
        command_content = self._bash_reader.get_next_line()
        command_arg = self._argument_reader.parse_argument(command_content)
        if len(command_arg) >= 1:
            command_type = command_arg.pop(0)
            if command_type == "create":
                return self._generate_create_message(command_arg)
            elif command_type == "show":
                return self._generate_show_message(command_arg)
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
        parser_args = self._module_tool["create_parser"].get_runtime_arguments(command_arg)
        if parser_args:
            mission_uuid, mission_info = str(uuid.uuid1()), self._get_default_mission_info(parser_args)
            message_detail = {"mission_info": mission_info}
            response_message = self._send_semantic_transform(mission_uuid, "create_command", message_detail)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_show_message(self, command_arg: list):
        parser_args = self._module_tool["universal_parser"].get_runtime_arguments(command_arg)
        if parser_args:
            if parser_args.all or parser_args.mission_uuid:
                mission_uuid = None if parser_args.all else parser_args.mission_uuid
                response_message = self._send_semantic_transform(mission_uuid, "show_command", None)
            else:
                response_message = self._send_universal_log(None, "console", self._mode_error_tips)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_start_message(self, command_arg: list):
        parser_args = self._module_tool["universal_parser"].get_runtime_arguments(command_arg)
        if parser_args:
            if parser_args.all or parser_args.mission_uuid:
                mission_uuid = None if parser_args.all else parser_args.mission_uuid
                response_message = self._send_semantic_transform(mission_uuid, "start_command", None)
            else:
                response_message = self._send_universal_log(None, "console", self._mode_error_tips)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_pause_message(self, command_arg: list):
        parser_args = self._module_tool["universal_parser"].get_runtime_arguments(command_arg)
        if parser_args:
            if parser_args.all or parser_args.mission_uuid:
                mission_uuid = None if parser_args.all else parser_args.mission_uuid
                response_message = self._send_semantic_transform(mission_uuid, "pause_command", None)
            else:
                response_message = self._send_universal_log(None, "console", self._mode_error_tips)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_delete_message(self, command_arg: list):
        parser_args = self._module_tool["delete_parser"].get_runtime_arguments(command_arg)
        if parser_args:
            if parser_args.all or parser_args.mission_uuid:
                mission_uuid = None if parser_args.all else parser_args.mission_uuid
                message_detail = {"with_file": parser_args.with_file}
                response_message = self._send_semantic_transform(mission_uuid, "delete_command", message_detail)
            else:
                response_message = self._send_universal_log(None, "console", self._mode_error_tips)
        else:
            response_message = self._send_universal_log(None, "console", self._param_error_tips)
        return {"success": True, "message": response_message}

    def _generate_unknown_message(self, command_type):
        exception_tips = "Unknown command type: {}".format(command_type)
        response_message = self._send_universal_log(None, "console", exception_tips)
        return {"success": True, "message": response_message}

    def _get_default_mission_info(self, mission_parameter):
        standard_mission_info = dict()
        target_link = self._get_url_after_quote(mission_parameter.url)
        standard_mission_info["target_link"] = target_link
        standard_mission_info["save_path"] = mission_parameter.output
        standard_mission_info["thread_count"] = mission_parameter.thread
        standard_mission_info["headers"] = self._generate_standard_headers(mission_parameter.headers)
        standard_mission_info["proxy"] = mission_parameter.proxy
        return standard_mission_info

    def _generate_standard_headers(self, headers_content):
        header_generator = HTTPHeaderGenerator(self._version_name)
        if headers_content and len(headers_content):
            return header_generator.generate_header_from_content(headers_content)
        else:
            return header_generator.generate_header_with_default_agent()

    @staticmethod
    def _get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/?#[]@!$&'()*+,;=%")

    def _send_semantic_transform(self, mission_uuid, message_type, message_detail):
        message_dict = self._generate_signal_template("thread-transform")
        message_dict["content"] = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        return message_dict

    def _send_universal_log(self, mission_uuid, message_type, content):
        message_dict = self._generate_signal_template("thread-log")
        message_detail = {"sender": "CommandHelper", "content": content}
        message_dict["content"] = self._generate_execute_detail(mission_uuid, message_type, message_detail)
        return message_dict

    @staticmethod
    def _generate_signal_template(receiver):
        return {"handle": "resend", "receiver": receiver, "content": {}}

    @staticmethod
    def _generate_execute_detail(mission_uuid, message_type, message_detail) -> dict:
        signal_detail = {"mission_uuid": mission_uuid, "message_type": message_type, "message_detail": message_detail}
        return {"signal_type": "execute", "signal_detail": signal_detail}
