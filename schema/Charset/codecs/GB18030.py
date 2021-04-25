#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/25 12:00
# Create User: NB-Dragon
from schema.Charset.handles.AsciiHandler import AsciiHandler


class GB18030(AsciiHandler):
    def __init__(self):
        super().__init__()
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\x81-\xFE][\x40-\x7E\x80-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\x81-\xFE][\x30-\x39][\x81-\xFE][\x30-\x39]", "length": 4})

    def detect(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        byte_string_template = self._generate_bytes_template(byte_string)
        for tmp_byte_string in byte_string_template:
            tmp_match_count = self._detect_match_count(tmp_byte_string)
            if tmp_match_count > match_length:
                match_length = tmp_match_count
        match_length += self._get_ascii_count(byte_string)
        return match_length / expect_length

    def _generate_bytes_template(self, byte_string: bytes):
        result_list = list()
        result_list.append(self._get_bytes_without_ascii(byte_string))
        return result_list
