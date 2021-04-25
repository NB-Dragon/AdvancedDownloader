#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
import re


class AsciiHandler(object):
    def __init__(self):
        self._rule_list = list()

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

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_count += rule["length"] * rule_match_length
        return match_count

    @staticmethod
    def _get_ascii_count(byte_string: bytes):
        return len(re.findall(b"[\x00-\x7F]", byte_string))

    @staticmethod
    def _get_bytes_without_ascii(byte_string: bytes):
        return b"".join(re.findall(b"[^\x00-\x7F]", byte_string))

    @staticmethod
    def _split_in_length(content, length):
        return [content[i:i + length] for i in range(0, len(content), length)]
