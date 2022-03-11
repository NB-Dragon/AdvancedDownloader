#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/05/01 18:00
# Create User: NB-Dragon
import re
from core.charset.CharsetDetector import CharsetDetector


class HTTPContentDisposition(object):
    def __init__(self):
        self._charset_detector = CharsetDetector()

    """
    Refer link: https://www.rfc-editor.org/rfc/rfc6266.html#section-4.1
    """

    def get_disposition_result(self, content_disposition: str):
        disposition_parm = [item.strip() for item in content_disposition.split(";")]
        disposition_type = disposition_parm.pop(0)
        disposition_decode_parm = self._decode_disposition_param(disposition_parm)
        self._choose_the_best_token(disposition_decode_parm)
        return {"type": disposition_type, "param": disposition_decode_parm}

    """
    Refer link: https://www.rfc-editor.org/rfc/rfc5987#section-3.2
    """

    def _decode_disposition_param(self, param_list):
        result_dict = dict()
        for parm_item in param_list:
            token, value = [item.strip() for item in parm_item.split("=", 1)]
            token, charset = token.lower(), None
            if token.endswith("*") and "'" in value:
                charset, language, value = value.split("'", 2)
            elif re.match("^\"(.*)\"$", value):
                value = re.sub("^\"(.*)\"$", "\\1", value)
            value = self._decode_correct_charset(value, charset)
            result_dict[token] = value
        return result_dict

    def _decode_correct_charset(self, content, charset=None):
        try:
            encode_content = content.encode("iso-8859-1")
            encode_content = self._replace_url_encoding_to_hex(encode_content)
            if charset is None:
                charset = self._detect_correct_charset(encode_content)
            return encode_content.decode(charset)
        except (UnicodeEncodeError, LookupError):
            return content

    @staticmethod
    def _replace_url_encoding_to_hex(content: bytes):
        url_data_list = list(set(re.findall(b"(%[0-9a-fA-F]{2})", content)))
        for url_data_item in url_data_list:
            hex_string = bytes.fromhex(url_data_item.decode()[1:])
            content = content.replace(url_data_item, hex_string)
        return content

    def _detect_correct_charset(self, byte_string):
        result = self._charset_detector.detect(byte_string)
        return "iso-8859-1" if result["confidence"] < 0.5 else result["encoding"]

    @staticmethod
    def _choose_the_best_token(original_dict):
        multi_token = []
        for key in original_dict.keys():
            key_with_star = "{}*".format(key)
            if key_with_star in original_dict:
                multi_token.append((key, key_with_star))
        for multi_token_item in multi_token:
            key, key_with_star = multi_token_item
            original_dict[key] = original_dict.pop(key_with_star)
