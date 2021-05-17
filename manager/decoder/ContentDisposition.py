#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/5/16 12:00
# Create User: NB-Dragon
import re
import urllib.parse
from schema.charset import chardet


class ContentDisposition(object):
    @staticmethod
    def parse_unquote_value(content):
        while re.findall("%[0-9a-fA-F]{2}", content):
            content = urllib.parse.unquote(content)
        return content

    def generate_parm_dict(self, content):
        disposition_parm = [item.strip() for item in content.split(";")]
        disposition_type = disposition_parm.pop(0)
        disposition_decode_parm = self._decode_disposition_param(disposition_parm)
        disposition_decode_parm = self._handle_indexing_param(disposition_decode_parm)
        self._combine_same_token(disposition_decode_parm, "**", "*")
        self._combine_same_token(disposition_decode_parm, "*", "")
        return {"type": disposition_type, "param": disposition_decode_parm}

    def _decode_disposition_param(self, param_list):
        result_dict = dict()
        for parm_item in param_list:
            token, value = parm_item.split("=", 1)
            value = self._quote_value(value)
            if token.endswith("*") and "'" in value:
                charset, language, content = value.split("'", 2)
                value = self._decode_correct_charset(content, charset)
            else:
                value = self._decode_correct_charset(value)
            result_dict[token] = self.parse_unquote_value(value)
        return result_dict

    @staticmethod
    def _handle_indexing_param(parm_dict):
        indexing_dict = dict()
        result_dict = dict()
        for key, value in parm_dict.items():
            match_result = re.findall("^([^*]+)\\*(\\d+)(\\*?)$", key)
            if len(match_result):
                result = match_result[0]
                token_name, index, star = result
                if token_name not in indexing_dict:
                    indexing_dict[token_name] = dict()
                indexing_dict[token_name][index] = parm_dict[key]
            else:
                result_dict[key] = value
        for key, value in indexing_dict.items():
            value_list = dict(sorted(value.items())).values()
            result_dict["{}**".format(key)] = "".join(value_list)
        return result_dict

    @staticmethod
    def _combine_same_token(original_dict, from_end, to_end):
        from_dict_key = [key[:-len(from_end)] for key in original_dict.keys() if key.endswith(from_end)]
        for key in from_dict_key:
            from_key = "{}{}".format(key, from_end)
            to_key = "{}{}".format(key, to_end)
            original_dict[to_key] = original_dict.pop(from_key)

    @staticmethod
    def _quote_value(content):
        return eval(content) if re.findall("^\".*\"$", content) else content

    def _decode_correct_charset(self, content, charset=None):
        try:
            encode_content = content.encode("iso-8859-1")
            if charset is None:
                charset = self._detect_correct_charset(encode_content)
            return encode_content.decode(charset)
        except (UnicodeEncodeError, LookupError):
            return content

    @staticmethod
    def _detect_correct_charset(byte_string):
        result = chardet.detect(byte_string)
        return "iso-8859-1" if result["confidence"] < 0.5 else result["encoding"]
