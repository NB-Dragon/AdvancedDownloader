class RequestDictionary(object):
    @staticmethod
    def get_default_user_agent():
        user_agent_list = list()
        user_agent_list.append("Mozilla/5.0")
        return "User-Agent: {}".format(" ".join(user_agent_list))

    @staticmethod
    def make_dict_from_cookies(content):
        each_value_list = content.split(";")
        result_dict = {}
        for key_value in each_value_list:
            if key_value == "": continue
            key, value = key_value.split("=", 1)
            result_dict[key.strip()] = value.strip()
        return result_dict

    @staticmethod
    def make_dict_from_headers(content):
        each_value_list = content.split("\n")
        result_dict = {}
        for key_value in each_value_list:
            if key_value == "": continue
            key, value = key_value.split(":", 1)
            result_dict[key.strip()] = value.strip()
        return result_dict
