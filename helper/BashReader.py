#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/03/01 20:00
# Create User: NB-Dragon
class BashReader(object):
    def get_next_line(self):
        state_dict = {"escape_string": False, "single_quote": False, "double_quote": False}
        result = ""
        while True:
            tmp_line, index = input(), 0
            while index < len(tmp_line):
                if self._judge_all_false(state_dict):
                    if tmp_line[index] == "\"":
                        index, scan_result = self._scan_double_quote_string(tmp_line, index, state_dict)
                    elif tmp_line[index] == "\'":
                        index, scan_result = self._scan_single_quote_string(tmp_line, index, state_dict)
                    else:
                        index, scan_result = self._scan_no_quote_string(tmp_line, index, state_dict)
                else:
                    if state_dict["double_quote"]:
                        index, scan_result = self._scan_double_quote_string(tmp_line, index, state_dict)
                    elif state_dict["single_quote"]:
                        index, scan_result = self._scan_single_quote_string(tmp_line, index, state_dict)
                    else:
                        index, scan_result = self._scan_no_quote_string(tmp_line, index, state_dict)
                state_dict.update(scan_result)
            if self._judge_all_false(state_dict):
                result = "{}{}".format(result, tmp_line)
                break
            else:
                result = "{}{}\n".format(result, tmp_line)
            state_dict["escape_string"] = False
        return result

    @staticmethod
    def _scan_no_quote_string(content: str, index: int, previous_result: dict):
        escape_string = previous_result["escape_string"]
        while index < len(content):
            if content[index] == "\\":
                escape_string = False if escape_string else True
            elif content[index] in ["\"", "\'"]:
                break
            elif escape_string:
                escape_string = False
            index += 1
        return index, {"escape_string": escape_string}

    @staticmethod
    def _scan_single_quote_string(content: str, index: int, previous_result: dict):
        escape_string, single_quote = previous_result["escape_string"], previous_result["single_quote"]
        while index < len(content):
            if content[index] == "\'":
                single_quote = False if single_quote else True
                if single_quote is False:
                    index += 1
                    break
            index += 1
        return index, {"escape_string": escape_string, "single_quote": single_quote}

    @staticmethod
    def _scan_double_quote_string(content: str, index: int, previous_result: dict):
        escape_string, double_quote = previous_result["escape_string"], previous_result["double_quote"]
        while index < len(content):
            if content[index] == "\"":
                if escape_string:
                    escape_string = False
                else:
                    double_quote = False if double_quote else True
                if double_quote is False:
                    index += 1
                    break
            elif content[index] == "\\":
                escape_string = False if escape_string else True
            else:
                if escape_string:
                    escape_string = False
            index += 1
        return index, {"escape_string": escape_string, "double_quote": double_quote}

    @staticmethod
    def _judge_all_false(state_dict):
        false_value = [item for item in state_dict.values() if item is False]
        return len(false_value) == len(state_dict)
