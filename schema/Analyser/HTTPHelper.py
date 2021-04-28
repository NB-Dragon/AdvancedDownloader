#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2021/1/25 10:00
# Create User: NB-Dragon
import os
import re
import schema.Charset.chardet as chardet
import urllib.parse
import urllib3
from tool.RuntimeOperator import RuntimeOperator


class HTTPHelper(object):
    @staticmethod
    def get_download_file_requirement(headers, link):
        filename = HeaderAnalyser().get_download_file_name(headers, link)
        filesize = HeaderAnalyser().get_download_file_size(headers)
        range_header = HeaderAnalyser().judge_download_range_skill(headers)
        range_skill = isinstance(filesize, int) and range_header
        return {"filename": filename, "filesize": filesize, "range": range_skill}

    @staticmethod
    def get_url_after_quote(link):
        return urllib.parse.quote(link, safe=":/?#[]@!$&'()*+,;=%")

    @staticmethod
    def get_request_pool_manager(alive_count):
        cert_pem_file = RuntimeOperator().get_static_cert_path()
        return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert_pem_file, maxsize=alive_count, timeout=15)


class HeaderAnalyser(object):
    def get_download_file_name(self, headers, link):
        content_disposition = headers.get("content-disposition")
        content_type = headers.get("content-type")
        if content_disposition and "filename" in content_disposition:
            result = ContentDispositionParser().generate_parm_dict(content_disposition)
            filename = result["param"]["filename"]
        else:
            link_parse_result = urllib.parse.urlparse(link)
            filename = link_parse_result.path.split("/")[-1]
            filename = ContentDispositionParser.parse_unquote_value(filename)
        filename = self._get_default_file_name(content_type, filename)
        return filename

    def _get_default_file_name(self, content_type, current_name):
        if "." in current_name:
            name, postfix = os.path.splitext(current_name)
        elif len(current_name):
            name, postfix = current_name, ".dat"
        else:
            name, postfix = "unknown", ".dat"
        correct_postfix = self._find_correct_postfix(content_type)
        postfix = correct_postfix or postfix
        return "{}{}".format(name, postfix)

    @staticmethod
    def _find_correct_postfix(content_type):
        default_postfix = RuntimeOperator().get_content_type_postfix()
        for key, value in default_postfix.items():
            if key in content_type:
                return value
        return None

    @staticmethod
    def get_download_file_size(headers):
        if "content-range" in headers:
            return int(re.findall("bytes \\d+-\\d+/(\\d+)", headers["content-range"])[0])
        elif "content-length" in headers:
            return int(headers.get("content-length"))
        else:
            return None

    @staticmethod
    def judge_download_range_skill(headers):
        return "content-range" in headers or "accept-ranges" in headers


class ContentDispositionParser(object):
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


class HeaderGenerator(object):
    @staticmethod
    def get_header_user_agent():
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0 (X11; Linux x86_64)")
        user_agent_list.append("AppleWebKit/537.36 (KHTML, like Gecko)")
        user_agent_list.append("AdvancedDownloader/0.5.9")
        return {"User-Agent": " ".join(user_agent_list)}

    @staticmethod
    def get_header_baidu_net_disk(bduss: str):
        headers = dict()
        headers["User-Agent"] = "netdisk"
        headers["Cookie"] = "BDUSS={}".format(bduss)
        return headers

    @staticmethod
    def make_dict_from_headers(content):
        each_value_list = content.split("\n")
        result_dict = {}
        for key_value in each_value_list:
            if key_value == "": continue
            key, value = key_value.split(":", 1)
            result_dict[key.strip()] = value.strip()
        return result_dict
