#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/01 00:00
# Create User: NB-Dragon
import argparse
import time


class DeleteParser(object):
    def __init__(self):
        self._continue_checking = True

    def get_runtime_arguments(self, argument_content=None):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("--all", action="store_true", help="Show the mission summary information.")
            parser.add_argument("--mission_uuid", dest='mission_uuid', help="Show the specific mission info.")
            parser.add_argument("--with-file", action="store_true", help="Change to true if you want to delete file.")
            args = parser.parse_args(argument_content)
            return args if self._check_input_args(args) else None
        except SystemExit:
            return None

    def _check_input_args(self, args):
        return self._continue_checking

    def _send_error_message(self, message):
        self._continue_checking = False
        self._make_message_and_send(message)

    @staticmethod
    def _make_message_and_send(content):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        output_content = "[{}][{}]: {}".format(current_time, "ParserHelper", content)
        print(output_content)
