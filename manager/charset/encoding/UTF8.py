#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
from manager.charset.encoding.ASCII import ASCII


class UTF8(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "UTF8"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\xC2-\xDF][\x80-\xBF]", "length": 2})
        self._rule_list.append({"regex": b"|".join(self._generate_regex_with_length_3()), "length": 3})
        self._rule_list.append({"regex": b"|".join(self._generate_regex_with_length_4()), "length": 4})

    @staticmethod
    def _generate_regex_with_length_3():
        result_list = list()
        result_list.append(b"[\xE0][\xA0-\xBF][\x80-\xBF]")
        result_list.append(b"[\xE1-\xEC][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xED][\x80-\x9F][\x80-\xBF]")
        result_list.append(b"[\xEE-\xEF][\x80-\xBF][\x80-\xBF]")
        return result_list

    @staticmethod
    def _generate_regex_with_length_4():
        result_list = list()
        result_list.append(b"[\xF0][\x90-\xBF][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xF1-\xF3][\x80-\xBF][\x80-\xBF][\x80-\xBF]")
        result_list.append(b"[\xF4][\x80-\x8F][\x80-\xBF][\x80-\xBF]")
        return result_list
