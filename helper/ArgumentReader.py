#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/03/01 20:00
# Create User: NB-Dragon
import re


class ArgumentReader(object):
    def __init__(self):
        self._no_quote_regex = re.compile("^(?:[^\\s'\"\\\\]|\\\\(?:\\\\\\\\)*[\\s\\S]|\\\\\\\\)*")
        self._single_quote_regex = re.compile("^\'[^\']*\'")
        self._double_quote_regex = re.compile("^\"(?:[^\"\\\\]|\\\\(?:\\\\\\\\)*[\\s\\S]|\\\\\\\\)*\"")

    def parse_argument(self, content: str):
        param_list, tmp_data, = [], []
        current_index, content_length = 0, len(content)
        while current_index < content_length:
            if content[current_index] == "\"":
                match_result, current_index = self._get_double_quote_item(content, current_index)
                tmp_data.append(match_result)
            elif content[current_index] == "\'":
                match_result, current_index = self._get_single_quote_item(content, current_index)
                tmp_data.append(match_result)
            else:
                match_result, current_index = self._get_no_quote_item(content, current_index)
                tmp_data.append(match_result)
            if current_index == content_length or content[current_index] == " ":
                param_list.append("".join(tmp_data))
                tmp_data.clear()
                current_index += 1
        self._remove_empty_param(param_list)
        return param_list

    def _get_no_quote_item(self, content: str, index: int):
        match_result = self._no_quote_regex.findall(content[index:])
        if len(match_result):
            final_result = match_result[0]
            final_result = final_result.replace("\\\\", "\\")
            final_result = final_result.replace("\\\n", "")
            final_result = re.sub("\\\\([^\\\\])", "\1", final_result)
            return final_result, index + len(match_result[0])
        else:
            return "", index

    def _get_single_quote_item(self, content: str, index: int):
        match_result = self._single_quote_regex.findall(content[index:])
        if len(match_result):
            final_result = match_result[0]
            return final_result[1:-1], index + len(match_result[0])
        else:
            return "", index

    def _get_double_quote_item(self, content: str, index: int):
        match_result = self._double_quote_regex.findall(content[index:])
        if len(match_result):
            final_result = match_result[0]
            final_result = final_result.replace("\\\\", "\\")
            final_result = final_result.replace("\\\n", "")
            final_result = final_result.replace("\\\"", "\"")
            return final_result[1:-1], index + len(match_result[0])
        else:
            return "", index

    @staticmethod
    def _remove_empty_param(param_list: list):
        while "" in param_list:
            param_list.remove("")
