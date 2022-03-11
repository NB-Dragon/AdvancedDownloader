#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
from core.charset.encoding.ASCII import ASCII


class GBK(ASCII):
    def __init__(self):
        super().__init__()
        self._charset_name = "GBK"
        self._ascii_filter_rule = b"[\x00-\x3F]"
        self._ascii_extend_rule = b"[\x40-\x7F]"
        self._ascii_outside_rule = b"[^\x00-\x3F]+"
        self._init_specification()

    def _init_specification(self):
        self._rule_list.append({"regex": self._generate_normal_length_2(), "length": 2})

    def _generate_normal_length_2(self):
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
        return self._combine_list_rule(result_list)

    @staticmethod
    def _combine_list_rule(byte_rule_list):
        return b"|".join(byte_rule_list)
