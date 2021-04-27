#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
import re

from schema.Charset.Handles.AsciiHandler import AsciiHandler


class GBK(AsciiHandler):
    def __init__(self):
        super().__init__()
        self._charset_name = "GBK"
        self._ascii_filter_rule = b"[\x00-\x3F]"
        self._bytes_without_ascii_rule = b"[^\x00-\x3F]+"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"|".join(self._generate_regex_with_length_2()), "length": 2})

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            tmp_result = re.findall(rule["regex"], byte_string)
            match_count += rule["length"] * len(tmp_result)
            byte_string = re.sub(rule["regex"], b"\x00", byte_string)
        match_count += len(re.findall(b"[\x40-\x7F]", byte_string))
        return match_count

    @staticmethod
    def _generate_regex_with_length_2():
        result_list = list()
        result_list.append(b"[\x81-\xA0][\x40-\x7E\x80-\xFE]")
        result_list.append(b"[\xA1][\xA1-\xFE]")
        result_list.append(b"[\xA2][\xA1-\xAA\xB1-\xE2\xE5-\xEE\xF1-\xFC]")
        result_list.append(b"[\xA3][\xA1-\xFE]")
        result_list.append(b"[\xA4][\xA1-\xF3]")
        result_list.append(b"[\xA5][\xA1-\xF6]")
        result_list.append(b"[\xA6][\xA1-\xB8\xC1-\xD8\xE0-\xEB\xEE-\xF2\xF4\xF5]")
        result_list.append(b"[\xA7][\xA1-\xC1\xD1-\xF1]")
        result_list.append(b"[\xA8][\x40-\x7E\x80-\x95\xA1-\xBB\xBD\xBE\xC0\xC5-\xE9]")
        result_list.append(b"[\xA9][\x40-\x57\x59\x5A\x5C\x60-\x7E\x80-\x88\x96\xA4-\xEF]")
        result_list.append(b"[\xAA-\xAF][\x40-\x7E\x80-\xA0]")
        result_list.append(b"[\xB0-\xD6][\x40-\x7E\x80-\xFE]")
        result_list.append(b"[\xD7][\x40-\x7E\x80-\xF9]")
        result_list.append(b"[\xD8-\xF7][\x40-\x7E\x80-\xFE]")
        result_list.append(b"[\xF8-\xFE][\x40-\x7E\x80-\xA0]")
        return result_list
