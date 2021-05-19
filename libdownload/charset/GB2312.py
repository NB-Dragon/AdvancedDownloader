#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
from libdownload.charset.ASCII import ASCII


class GB2312(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "GB2312"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"|".join(self._generate_regex_with_length_2()), "length": 2})

    @staticmethod
    def _generate_regex_with_length_2():
        result_list = list()
        result_list.append(b"[\xA1][\xA1-\xFE]")
        result_list.append(b"[\xA2][\xB1-\xE2\xE5-\xEE\xF1-\xFC]")
        result_list.append(b"[\xA3][\xA1-\xFE]")
        result_list.append(b"[\xA4][\xA1-\xF3]")
        result_list.append(b"[\xA5][\xA1-\xF6]")
        result_list.append(b"[\xA6][\xA1-\xB8\xC1-\xD8]")
        result_list.append(b"[\xA7][\xA1-\xC1\xD1-\xF1]")
        result_list.append(b"[\xA8][\xA1-\xBA\xC5-\xE9]")
        result_list.append(b"[\xA9][\xA4-\xEF]")
        result_list.append(b"[\xB0-\xD6][\xA1-\xFE]")
        result_list.append(b"[\xD7][\xA1-\xF9]")
        result_list.append(b"[\xD8-\xF7][\xA1-\xFE]")
        return result_list
