#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2022/02/05 10:00
# Create User: NB-Dragon
class NetworkSectionHelper(object):
    def get_download_section(self, current_section_list, expect_section_count):
        """
        @:param current_section_list: [[min1, max1], [min2, max2], ...];
        @:param expect_section_count: expect_section_count > 0.
        """
        expect_section_count = max(len(current_section_list), expect_section_count)
        section_sorted_list = sorted(current_section_list, key=lambda x: x[1] - x[0], reverse=True)
        section_size_list = [self._calculate_section_size(item) for item in section_sorted_list]
        section_weight_list = self._generate_section_weight_list(section_size_list, expect_section_count)
        return self._generate_section_with_weight(section_sorted_list, section_weight_list)

    def _generate_section_weight_list(self, section_size_list, maximum_weight):
        simple_weight_list = self._generate_simple_weight_list(section_size_list, maximum_weight)
        fine_tuned_weight_list = self._generate_fine_tuned_weight_list(simple_weight_list, maximum_weight)
        return fine_tuned_weight_list

    @staticmethod
    def _generate_simple_weight_list(section_size_list, maximum_weight):
        minimal_size = min(section_size_list)
        multiple_list = [item // minimal_size for item in section_size_list]
        current_weight = sum(multiple_list)
        if current_weight < maximum_weight:
            quotient, remainder = divmod(maximum_weight, current_weight)
            result_list, index = [item * quotient for item in multiple_list], 0
            while remainder > 0:
                real_weight = min(remainder, multiple_list[index])
                result_list[index] += real_weight
                remainder -= real_weight
                index += 1
            return result_list
        else:
            return multiple_list

    def _generate_fine_tuned_weight_list(self, section_multiple_list, maximum_weight):
        if len(section_multiple_list) > 1:
            current_weight = sum(section_multiple_list)
            while current_weight > maximum_weight:
                max_number_list = sorted(set(section_multiple_list), reverse=True)[0:2]
                max_number_excess = max_number_list[0] - max_number_list[1]
                max_number_count = self._calculate_number_count(max_number_list[0], section_multiple_list)
                excess_weight = current_weight - maximum_weight
                real_sub_weight = min(max_number_excess * max_number_count, excess_weight)
                sub_operate_list = self._split_content_size(real_sub_weight, max_number_count, False)
                for index in range(len(sub_operate_list)):
                    section_multiple_list[index] -= sub_operate_list[index]
                current_weight = sum(section_multiple_list)
        return section_multiple_list

    def _generate_section_with_weight(self, section_sorted_list, section_weight_list):
        result_list = list()
        for index in range(len(section_sorted_list)):
            current_section, thread_count = section_sorted_list[index], section_weight_list[index]
            section_size = self._calculate_section_size(current_section)
            section_each_list = self._split_content_size(section_size, thread_count, True)
            result_list.extend(self._generate_section_list(current_section[0], section_each_list))
        return sorted(result_list, key=lambda x: x[0])

    @staticmethod
    def _split_content_size(content_size: int, thread_count: int, reverse):
        quotient, remainder = divmod(content_size, thread_count)
        result_list = [quotient] * thread_count
        result_list[0: remainder] = [quotient + 1] * remainder
        return sorted(result_list, reverse=reverse)

    @staticmethod
    def _generate_section_list(start_position: int, section_size_list: list):
        result_list = list()
        for section_size in section_size_list:
            if section_size != 0:
                end_position = start_position + section_size
                result_list.append([start_position, end_position - 1])
                start_position = end_position
        return result_list

    @staticmethod
    def _calculate_section_size(section_item: list):
        return section_item[1] - section_item[0] + 1

    @staticmethod
    def _calculate_number_count(expect_number: int, number_list: list):
        count = 0
        for item in number_list:
            if item == expect_number:
                count += 1
        return count
