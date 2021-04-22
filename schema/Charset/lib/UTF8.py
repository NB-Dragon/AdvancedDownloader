#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
import re


class UTF8(object):
    def __init__(self):
        self._rule_list = list()
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": b"[\x00-\x7F]", "length": 1})
        self._rule_list.append({"regex": b"[\xC0-\xDF][\x80-\xBF]{1}", "length": 2})
        self._rule_list.append({"regex": b"[\xE0-\xEF][\x80-\xBF]{2}", "length": 3})
        self._rule_list.append({"regex": b"[\xF0-\xF7][\x80-\xBF]{3}", "length": 4})
        self._rule_list.append({"regex": b"[\xF8-\xFB][\x80-\xBF]{4}", "length": 5})
        self._rule_list.append({"regex": b"[\xFC-\xFD][\x80-\xBF]{5}", "length": 6})

    def detect(self, byte_string: bytes):
        match_length = 0
        for rule in self._rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_length += rule["length"] * rule_match_length
        return match_length / len(byte_string)
