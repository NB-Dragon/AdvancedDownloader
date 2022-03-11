#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/15 18:00
# Create User: NB-Dragon
from core.charset.encoding.UNICODE import UNICODE


class UTF16(UNICODE):
    def __init__(self):
        super().__init__()
        self._charset_name = "UTF-16"
        self._init_specification()

    def _init_specification(self):
        self._rule_big_endian.append({"regex": self._generate_big_endian_length_2(), "length": 2})
        self._rule_big_endian.append({"regex": self._generate_big_endian_length_4(), "length": 4})
        self._rule_little_endian.append({"regex": self._generate_little_endian_length_2(), "length": 2})
        self._rule_little_endian.append({"regex": self._generate_little_endian_length_4(), "length": 4})

    def _generate_big_endian_length_2(self):
        result_list = list()
        result_list.append(b"[\x00-\xD7][\x00-\xFF]")
        result_list.append(b"[\xE0-\xFF][\x00-\xFF]")
        return self._combine_list_rule(result_list)

    def _generate_big_endian_length_4(self):
        result_list = list()
        result_list.append(b"[\xD8-\xDB][\x00-\xFF][\xDC-\xDF][\x00-\xFF]")
        return self._combine_list_rule(result_list)

    def _generate_little_endian_length_2(self):
        result_list = list()
        result_list.append(b"[\x00-\xFF][\x00-\xD7]")
        result_list.append(b"[\x00-\xFF][\xE0-\xFF]")
        return self._combine_list_rule(result_list)

    def _generate_little_endian_length_4(self):
        result_list = list()
        result_list.append(b"[\x00-\xFF][\xD8-\xDB][\x00-\xFF][\xDC-\xDF]")
        return self._combine_list_rule(result_list)

    @staticmethod
    def _combine_list_rule(byte_rule_list):
        return b"|".join(byte_rule_list)
