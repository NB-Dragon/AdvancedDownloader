#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
from core.charset.encoding.ASCII import ASCII


class UTF8(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "UTF-8"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\xC2-\xDF][\x80-\xBF]", "length": 2})
        self._rule_list.append({"regex": self._generate_normal_length_3(), "length": 3})
        self._rule_list.append({"regex": self._generate_normal_length_4(), "length": 4})

    def _generate_normal_length_3(self):
        result_list = list()
        result_list.append(b"[\xE0][\xA0-\xBF][\x80-\xBF]")
        result_list.append(b"[\xE1-\xEC][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xED][\x80-\x9F][\x80-\xBF]")
        result_list.append(b"[\xEE-\xEF][\x80-\xBF][\x80-\xBF]")
        return self._combine_list_rule(result_list)

    def _generate_normal_length_4(self):
        result_list = list()
        result_list.append(b"[\xF0][\x90-\xBF][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xF1-\xF3][\x80-\xBF][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xF4][\x80-\x8F][\x80-\xBF][\x80-\xBF]")
        return self._combine_list_rule(result_list)

    @staticmethod
    def _combine_list_rule(byte_rule_list):
        return b"|".join(byte_rule_list)
