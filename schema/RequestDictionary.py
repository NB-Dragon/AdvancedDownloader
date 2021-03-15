class RequestDictionary(object):
    @staticmethod
    def get_header_user_agent():
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0 (X11; Linux x86_64)")
        user_agent_list.append("AppleWebKit/537.36 (KHTML, like Gecko)")
        user_agent_list.append("AdvancedDownloader/0.5.5")
        return {"User-Agent": " ".join(user_agent_list)}

    @staticmethod
    def get_header_baidu_net_disk(bduss: str, stoken: str):
        headers = dict()
        headers["User-Agent"] = "netdisk"
        headers["Cookie"] = "BDUSS={}; STOKEN={}".format(bduss, stoken)
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
