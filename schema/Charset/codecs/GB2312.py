#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
from schema.Charset.LowerHandler import LowerHandler


class GB2312(LowerHandler):
    def __init__(self):
        super().__init__()
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\xA1][\xA1-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\xA2][\xB1-\xE2\xE5-\xEE\xF1-\xFC]", "length": 2})
        self._rule_list.append({"regex": b"[\xA3][\xA1-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\xA4][\xA1-\xF3]", "length": 2})
        self._rule_list.append({"regex": b"[\xA5][\xA1-\xF6]", "length": 2})
        self._rule_list.append({"regex": b"[\xA6][\xA1-\xB8\xC1-\xD8]", "length": 2})
        self._rule_list.append({"regex": b"[\xA7][\xA1-\xC1\xD1-\xF1]", "length": 2})
        self._rule_list.append({"regex": b"[\xA8][\xA1-\xBA\xC5-\xE9]", "length": 2})
        self._rule_list.append({"regex": b"[\xA9][\xA4-\xEF]", "length": 2})
        self._rule_list.append({"regex": b"[\xB0-\xD6][\xA1-\xFE]", "length": 2})
        self._rule_list.append({"regex": b"[\xD7][\xA1-\xF9]", "length": 2})
        self._rule_list.append({"regex": b"[\xD8-\xF7][\xA1-\xFE]", "length": 2})

    def detect(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        byte_string_template = self._generate_bytes_template(byte_string)
        self._adapt_current_charset_template(byte_string_template)
        for tmp_byte_string in byte_string_template:
            tmp_match_count = self._detect_match_count(tmp_byte_string)
            if tmp_match_count > match_length:
                match_length = tmp_match_count
        match_length += self._get_lower_count(byte_string)
        return match_length / expect_length

    def _generate_bytes_template(self, byte_string: bytes):
        result_list = list()
        result_list.append(self._get_bytes_without_lower(byte_string))
        result_list.append(self._get_bytes_without_lower(byte_string[1:]))
        return result_list

    def _adapt_current_charset_template(self, byte_string_list: list):
        for index in range(len(byte_string_list)):
            byte_string_item = byte_string_list[index]
            byte_string_item = b"|".join(self._split_in_length(byte_string_item, 2))
            byte_string_list[index] = byte_string_item

    @staticmethod
    def _split_in_length(content, length):
        return [content[i:i + length] for i in range(0, len(content), length)]
