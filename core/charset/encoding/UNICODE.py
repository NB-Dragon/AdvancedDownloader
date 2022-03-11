#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/01/15 18:00
# Create User: NB-Dragon
import re
import sys


class UNICODE(object):
    def __init__(self):
        self._rule_big_endian = list()
        self._rule_little_endian = list()
        self._charset_name = "UNICODE"

    def detect(self, byte_string: bytes):
        big_endian_confidence = self._detect_big_endian(byte_string)
        little_endian_confidence = self._detect_little_endian(byte_string)
        endian = self._get_encoding_endian(big_endian_confidence, little_endian_confidence)
        self._charset_name = "{}-{}".format(self._charset_name, endian)
        confidence = max(big_endian_confidence, little_endian_confidence)
        return {"encoding": self._charset_name, "confidence": confidence}

    def _detect_big_endian(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        match_length += self._detect_match_count(byte_string, self._rule_big_endian)
        return match_length / expect_length if expect_length else 0

    def _detect_little_endian(self, byte_string: bytes):
        expect_length, match_length = len(byte_string), 0
        match_length += self._detect_match_count(byte_string, self._rule_little_endian)
        return match_length / expect_length if expect_length else 0

    @staticmethod
    def _detect_match_count(byte_string: bytes, detect_rule_list):
        match_count = 0
        for rule in detect_rule_list:
            rule_match_length = len(re.findall(rule["regex"], byte_string))
            match_count += rule["length"] * rule_match_length
            byte_string = re.sub(rule["regex"], b"", byte_string)
        return match_count

    @staticmethod
    def _get_encoding_endian(big_endian_confidence, little_endian_confidence):
        if big_endian_confidence > little_endian_confidence:
            return "BE"
        elif big_endian_confidence < little_endian_confidence:
            return "LE"
        else:
            """
            Refer document: https://www.rfc-editor.org/rfc/rfc2781.html#section-4.3
                Text labelled with the "UTF-16" charset might be serialized in either
                big-endian or little-endian order. If the first two octets of the
                text is 0xFE followed by 0xFF, then the text can be interpreted as
                being big-endian. If the first two octets of the text is 0xFF
                followed by 0xFE, then the text can be interpreted as being little-
                endian. If the first two octets of the text is not 0xFE followed by
                0xFF, and is not 0xFF followed by 0xFE, then the text SHOULD be
                interpreted as being big-endian.
            I think the best way to detect is to follow the system.
            """
            return "LE" if sys.byteorder == "little" else "BE"
