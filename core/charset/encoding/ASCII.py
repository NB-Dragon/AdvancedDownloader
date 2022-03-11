#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import re


class ASCII(object):
    def __init__(self):
        self._rule_list = list()
        self._charset_name = "ASCII"
        self._ascii_filter_rule = b"[\x00-\x7F]"
        self._ascii_extend_rule = None
        # ascii_filter_rule + ascii_extend_rule = b"[\x00-\x7F]"
        self._ascii_outside_rule = b"[^\x00-\x7F]+"

    def detect(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        byte_string_template = self._get_bytes_without_ascii(byte_string)
        for tmp_byte_string in byte_string_template:
            match_length += self._detect_match_count(tmp_byte_string)
        match_length += self._get_ascii_count(byte_string)
        confidence = match_length / expect_length if expect_length else 0
        return {"encoding": self._charset_name, "confidence": confidence}

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_count += rule["length"] * rule_match_length
            byte_string = re.sub(rule["regex"], b"\x00", byte_string)
        if self._ascii_extend_rule:
            match_count += len(re.findall(self._ascii_extend_rule, byte_string))
        return match_count

    def _get_bytes_without_ascii(self, byte_string: bytes):
        return re.findall(self._ascii_outside_rule, byte_string)

    def _get_ascii_count(self, byte_string: bytes):
        return len(re.findall(self._ascii_filter_rule, byte_string))
