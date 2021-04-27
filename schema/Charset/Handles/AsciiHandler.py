#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
import re


class AsciiHandler(object):
    def __init__(self):
        self._rule_list = list()
        self._charset_name = "ascii"
        self._ascii_filter_rule = b"[\x00-\x7F]"
        self._bytes_without_ascii_rule = b"[^\x00-\x7F]+"

    def detect(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        byte_string_template = self._generate_bytes_template(byte_string)
        for tmp_byte_string in byte_string_template:
            match_length += self._detect_match_count(tmp_byte_string)
        match_length += self._get_ascii_count(byte_string)
        return {"charset": self._charset_name, "confidence": match_length / expect_length}

    def _generate_bytes_template(self, byte_string: bytes):
        return self._get_bytes_without_ascii(byte_string)

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_count += rule["length"] * rule_match_length
        return match_count

    def _get_ascii_count(self, byte_string: bytes):
        return len(re.findall(self._ascii_filter_rule, byte_string))

    def _get_bytes_without_ascii(self, byte_string: bytes):
        return re.findall(self._bytes_without_ascii_rule, byte_string)

    @staticmethod
    def _split_in_length(content, length):
        return [content[i:i + length] for i in range(0, len(content), length)]
