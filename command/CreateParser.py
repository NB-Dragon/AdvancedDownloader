#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import argparse
import os
import time
from core.util.HTTPHeaderGenerator import HTTPHeaderGenerator


class CreateParser(object):
    def __init__(self, version_name):
        self._version_name = version_name
        self._header_generator = HTTPHeaderGenerator(version_name)
        self._continue_checking = True

    def get_runtime_arguments(self, argument_content=None):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-v", "--version", action="version", version=self._version_name)
            parser.add_argument("--url", dest='url', required=True, help="URL to connect to the resource.")
            parser.add_argument("--output", dest='output', required=True, help="The path to save without file name.")
            parser.add_argument("--thread", dest='thread', default=1, type=int, help="The maximum number of threads.")
            parser.add_argument("--headers", dest='headers', help="The request headers.")
            parser.add_argument("--proxy", dest='proxy', help="The request proxy.")
            args = parser.parse_args(argument_content)
            return args if self._check_input_args(args) else None
        except SystemExit:
            return None

    def _check_input_args(self, args):
        if not self._check_output_path_write(args.output):
            self._send_error_message("The output path does not exist or cannot be written.")
        args.headers = self._format_headers(args.headers)
        return self._continue_checking

    @staticmethod
    def _check_output_path_write(output_path):
        return os.access(output_path, os.F_OK) and os.access(output_path, os.W_OK)

    def _format_headers(self, headers_content):
        if headers_content and len(headers_content):
            return self._header_generator.generate_header_from_content(headers_content)
        else:
            return self._header_generator.generate_header_with_default_agent()

    def _send_error_message(self, message):
        self._continue_checking = False
        self._make_message_and_send(message)

    @staticmethod
    def _make_message_and_send(content):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        output_content = "[{}][{}]: {}".format(current_time, "ParserHelper", content)
        print(output_content)
