#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/4/22 18:00
# Create User: NB-Dragon
import re


class LowerHandler(object):
    def __init__(self):
        self._rule_list = list()

    def _detect_match_count(self, byte_string: bytes):
        match_count = 0
        for rule in self._rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_count += rule["length"] * rule_match_length
        return match_count

    @staticmethod
    def _get_lower_count(byte_string: bytes):
        return len(re.findall(b"[\x00-\x7F]", byte_string))

    @staticmethod
    def _get_bytes_without_lower(byte_string: bytes):
        return b"".join(re.findall(b"[^\x00-\x7F]", byte_string))
