#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-10 14:27:37
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
from collections import defaultdict


def get_dict_yaml_header(name: str, version: str, name_zh: str, desc: str) -> str:
    yaml_header = f"""# Rime dictionary
# encoding: utf-8
# https://github.com/Litles/rime-xingma-sentence
# 【名称】 {name_zh}
# 【描述】 {desc}
---
name: {name}
version: "{version}"
sort: by_weight
use_preset_vocabulary: false
columns:
  - text
  - code
  - weight
...
"""
    return yaml_header


def load_word_freq(file: str) -> dict:
    """加载字/词频表
    
    Args:
        file (str): 字/词频表文件
    
    Returns:
        dict: 以字/词为键, 以频数为值
    """
    dict_word_freq = defaultdict(int)
    with open(file, 'r', encoding='utf-8') as fr:
        set_alpha_num = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        for line in fr:
            word, freq = line.strip().split("\t")
            if set(word).isdisjoint(set_alpha_num):
                freq = 2 if int(freq) <= 0 else max(int(freq),3)  # occur then at least 3
                dict_word_freq[word] += freq  # 重复出现则累加
        return dict_word_freq


def load_char_code(*files: str, full_only: bool= True) -> dict:
    """加载单字码表
    
    Args:
        files (str): 单字码表文件(可以提供多个)
    
    Returns:
        dict: 以单字为键，以由编码构成的set为值
    """
    dict_char_codes = defaultdict(set)
    for file in files:
        with open(file, 'r', encoding='utf-8') as fr:
            for line in fr:
                if (not line.startswith("#")) and ("\t" in line):
                    # 1.从码表文件中提取编码
                    char, code_new, *trash = line.split(None, 2)
                    if len(code_new) == 1:
                        print("不支持一简:", line, end="")
                        continue
                    # code_new = code_new[:4]
                    # 2.开始处理 (只保留最全的编码, 支持一字多码, 比如有容错码)
                    if full_only and char in dict_char_codes:
                        for code in dict_char_codes[char]:
                            # 如果新来的码更全, 用它取代旧的
                            if code_new.startswith(code):
                                dict_char_codes[char].discard(code)
                                dict_char_codes[char].add(code_new)
                    else:
                        dict_char_codes[char].add(code_new)
    return dict_char_codes

def combine_code_and_freq(dict_char_codes: dict, dict_word_freq: dict, charset: set = set()) -> list:
    # 合并码表和词频数据
    list_char_freq = []
    if charset:
        for char, code in dict_char_codes.items():
            if char in charset:
                list_char_freq.append({
                    "char": char,
                    "code": list(code)[0], # 只取一个编码
                    "freq": dict_word_freq.get(char, 2)
                })
    else:
        for char, code in dict_char_codes.items():
            list_char_freq.append({
                "char": char,
                "code": list(code)[0],
                "freq": dict_word_freq.get(char, 2)
            })
    return list_char_freq

def adjust_zhi_char_freq(dict_char_freq: dict) -> None:
    # 1.手动调整部分字频
    dict_char_freq["世"], dict_char_freq["丨"] = dict_char_freq["丨"], dict_char_freq["世"]
    dict_char_freq["咸"], dict_char_freq["唔"] = dict_char_freq["唔"], dict_char_freq["咸"]
    dict_char_freq["运"], dict_char_freq["横"] = dict_char_freq["横"], dict_char_freq["运"]
    dict_char_freq["髟"], dict_char_freq["灬"] = dict_char_freq["灬"], dict_char_freq["髟"]
    dict_char_freq["购"], dict_char_freq["丸"] = dict_char_freq["丸"], dict_char_freq["购"]
    dict_char_freq["急"], dict_char_freq["绿"] = dict_char_freq["绿"], dict_char_freq["急"]
    # print(dict_char_freq["世"], dict_char_freq["丨"])
    
    # 2.调繁体字，确保大部分情况下简体先于繁体
    set_big5 = get_charset("字符集/Big5_汉字(包含兼容汉字).txt")
    set_tg = get_charset("字符集/G标_通规/通规（8105字）.txt")
    # set_gb2312 = get_charset("字符集/G标/GB2312汉字集.txt")  # GB2312中有少许繁体字(比如『後』)
    # 获取繁体、异体字集 (合计6千多个)
    with open("字符集/G标_通规/规范字与繁体字、异体字对照表.txt", 'r', encoding='utf-8') as fr:
        str_all = ""
        for line in fr:
            line = line.strip().rsplit("\t", 1)[1]
            str_all += re.sub(r"[\[\]\(\)\|]", "", line)
        set_fanyi = set(str_all)
    set_big5_only = (set_big5 | set_fanyi) - set_tg
    # 把通规和GB2312之外的字频调到6000名之外
    list_char_freq = [{"char": char, "freq": freq} for char, freq in dict_char_freq.items()]
    list_char_freq.sort(key=lambda d: d["freq"], reverse=True)
    bar = list_char_freq[5999]["freq"]
    freq_max = 2
    for d in list_char_freq:
        if d["char"] in set_big5_only:
            freq_max = d["freq"]
            break
    divisor = int(freq_max / bar) + 1  # 除数, 之后会有不等式 freq_max/divisor < bar
    for char in set_big5_only:
        if dict_char_freq.get(char, 2) >= 3:
            dict_char_freq[char] = max(int(dict_char_freq[char] / divisor), 3)
    print("已调整繁体字字频个数:", len(set_big5_only))

    # 3.调生僻字, 检查是否有本应5000开外(根据另一张字频表)的却在前3000
    list_char_freq = [{"char": char, "freq": freq} for char, freq in dict_char_freq.items()]
    list_char_freq.sort(key=lambda d: d["freq"], reverse=True)
    set_after5000 = get_charset("字词频/25亿字频表_5000之后.txt")
    set_after5000 -= set("怼熵薅咩吖欸粿焗焯蚝馕齁烷垚")
    set_after5000_proc = set()  # 实际需要处理的部分
    for i in range(3000):
        char = list_char_freq[i]["char"]
        if char in set_after5000:
            set_after5000_proc.add(char)
    # 开始处理
    bar = list_char_freq[4999]["freq"]
    for char in set_after5000_proc:
        if dict_char_freq.get(char, 2) >= 3:
            dict_char_freq[char] = bar - 1
    print("已调整生僻字字频个数:", len(set_after5000_proc))

def generate_dict_file_with_freq(file_in: str, file_freq: str) -> None:
    """为词库匹配词频，生成带词频的文件
    
    Args:
        file_in (str): 词库文件(一行一词)
        file_freq (str): 词频表
    """
    dict_word_freq = load_word_freq(file_freq)  # 加载词频表
    root, ext = os.path.splitext(file_in)
    file_out = root+"_with_freq"+ext  # 输出路径
    # 开始匹配并生成
    n_total = 0
    n_matched = 0
    with (
        open(file_in, 'r', encoding='utf-8') as fr,
        open(file_out, 'w', encoding='utf-8') as fw
    ):
        for line in fr:
            word = line.strip()
            if word:
                freq = 2
                if word in dict_word_freq:
                    freq = dict_word_freq[word]
                    n_matched += 1
                n_total += 1
                fw.write(f"{word}\t{freq}\n")
    print("已生成文件", file_out)
    print("总词条数", "匹配数", "未匹配数(已设频为2)", "匹配率")
    print(n_total, n_matched, n_total - n_matched, str(round(n_matched/n_total*100))+"%")

def print_chongma_statis(dict_code_chars: dict) -> None:
    """打印重码情况概览
    
    Args:
        dict_code_chars (dict): 以编码(比如"abcd")为键, 以字符列表(比如["我", "你"])为值
    """
    dct = dict_code_chars
    print("\n--- 重码情况统计 ---")
    print("总字数:", sum(len(dct[code]) for code in dct))
    print("总编码数:", len(dct))
    print("无重:", sum(1 for code in dct if len(dct[code]) == 1))
    print(
        "二重(组数):",
        str(sum(1 for code in dct if len(dct[code]) == 2))+"=",
        str(sum(1 for code in dct if len(dct[code]) == 2 and len(code) == 2))+"(2)",
        str(sum(1 for code in dct if len(dct[code]) == 2 and len(code) == 3))+"(3)",
        str(sum(1 for code in dct if len(dct[code]) == 2 and len(code) == 4))+"(4)",
        str(sum(1 for code in dct if len(dct[code]) == 2 and len(code) == 5))+"(5)"
    )
    print(
        "三重(组数):",
        str(sum(1 for code in dct if len(dct[code]) == 3))+"=",
        str(sum(1 for code in dct if len(dct[code]) == 3 and len(code) == 2))+"(2)",
        str(sum(1 for code in dct if len(dct[code]) == 3 and len(code) == 3))+"(3)",
        str(sum(1 for code in dct if len(dct[code]) == 3 and len(code) == 4))+"(4)",
        str(sum(1 for code in dct if len(dct[code]) == 3 and len(code) == 5))+"(5)"
    )
    print("四重以上(组数):", sum(1 for code in dct if len(dct[code]) > 3))
    print("最大重数:", max(len(dct[code]) for code in dct))
    # print("--- 3码重码明细 ---")
    # for code, chars in dct.items():
    #     if len(code) == 3 and len(chars) > 1:
    #         print(code, "".join(chars))
    # print("--- 4码重码明细 ---")
    # for code, chars in dct.items():
    #     if len(code) == 4 and len(chars) > 1:
    #         print(code, "".join(chars))
    # print("--- 四重以上明细 ---")
    # for code, chars in dct.items():
    #     if len(chars) > 3: 
    #         print(code, "".join(chars))

def get_charset(*files: str) -> set[str]:
    str_charset = ""
    for file in files:
        with open(file, 'r', encoding='utf-8') as fr:
            str_charset += re.sub(r"\s", "", fr.read())
            # str_charset += fr.read().replace("\r", "").replace("\n", "")
    return set(str_charset)

def compute_char_chongma(list_char_code: list, print_flag: bool = False, charset: set = set()) -> dict:
    """统计单字重码情况
    
    Args:
        list_char_code (list): 以dict(有"char"和"code"两个键)为元素的list
        print_flag (bool, optional): 是否打印统计结果, 默认False不打印
        file_charset (str, optional): 传入字符集文件则表示要限定分析的字符集范围, 默认不限定
    
    Returns:
        dict: 以编码(比如"abcd")为键, 以字符列表(比如["我", "你"])为值
    """
    # 1.统计
    if charset:
        # 开始统计(圈定分析范围)
        dict_code_chars = defaultdict(list)
        for d in list_char_code:
            if d["char"] in charset:
                dict_code_chars[d["code"]].append(d["char"])
    else:
        # 开始统计
        dict_code_chars = defaultdict(list)
        for d in list_char_code:
                dict_code_chars[d["code"]].append(d["char"])
    # 2.输出统计结果
    if print_flag:
        print_chongma_statis(dict_code_chars)
    return dict_code_chars


def generate_dict_yaml_ciku(
        file_in: str,
        dict_char_codes: dict,
        dict_word_freq: dict = dict(),
        dict_meta: dict = dict(),
        dir_out: str = ""
    ) -> None:
    # 1.get yaml header
    meta_default = {
        "name": "xxx",
        "version": "1.0",
        "name_zh": "词库名称",
        "desc": "词库描述"
    }
    if not dict_meta:
        dict_meta = dict(meta_default)
        dict_name = os.path.split(file_in)[1].rsplit(".dict.yaml", 1)[0]  # 从输入文件名判断
        dict_meta["name"] = dict_name
    yaml_header = get_dict_yaml_header(*dict_meta.values())
    # 2.get output path
    if not dir_out:
        dir_out = "out_yaml"
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    file_out = os.path.join(dir_out, dict_meta["name"]+".dict.yaml")
    # 3.start to convert
    convert_dict_yaml_file(file_in, file_out, dict_char_codes, dict_word_freq, yaml_header)


def convert_dict_yaml_file(
        yaml_file_in: str,
        yaml_file_out: str,
        dict_char_codes: dict,
        dict_word_freq: dict,
        yaml_header: str = ""
    ) -> None:
    """生成整句版码表文件(从yaml文件提取词条)
    
    Args:
        yaml_file_in (str): 包含词条的yaml文件(即待转换文件)
        yaml_file_out (str): 输出yaml文件(即结果文件)
        dict_char_codes (dict): 单字编码表dict, 一个可多编码(比如 "我": ("a", "abc"))
        dict_word_freq (dict): 词频表dict
        yaml_header (str): yaml文件描述
    """
    str_result = ""
    lines = []
    yaml_file_flag = False
    # 开始处理
    print("开始处理", yaml_file_in)
    with open(yaml_file_in, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
        line_1st = lines[0].lstrip()
        if line_1st.startswith("#") and "ime" in line_1st:
            yaml_file_flag = True
    words = set()
    for line in lines:
        line = line.strip()
        # 0.预处理
        # (a)注释行不用处理
        if yaml_file_flag:
            if line.startswith("#") or ("\t" not in line):
                # str_result += line  # 照搬注释行
                continue
        else:
            if line.startswith("#") or line.strip() == "":
                # str_result += line  # 照搬注释行
                continue
        word = line.split('\t')[0]  # 第一列，即单词（字或词）
        # (b)该单词是否已被处理过 (跳过), 也跳过单字
        if len(word) < 2 or (word in words):
            continue
        # (c)检查单词中是否包含超纲的字（即无编码）, 超纲则丢弃该单词
        for char in word:
            if char not in dict_char_codes:
                print(f"缺失 \"{char}\" 字的编码，已跳过该词: {word}")
                continue

        # 1.形成单词的编码 (用单字编码拼接)
        codes_of_chars = []
        for char in word:
            set_code = dict_char_codes[char]
            char_code = ','.join(code for code in set_code)  # .ljust(4, '0')  bbbb,cccc
            codes_of_chars.append(char_code)
        word_code = ' '.join(codes_of_chars)  # aaaa bbbb,cccc dddd

        # 2.匹配字词频
        freq = 0
        if word in dict_word_freq:
            freq = dict_word_freq[word]
        freq = 2 if int(freq) <= 0 else max(int(freq),3)  # occur then at least 3
        str_result += f"{word}\t{word_code}\t{freq}\n"
        words.add(word)  # 记录已处理过的词
    # 输出到文件
    with open(yaml_file_out, 'w', encoding='utf-8') as fw:
        if not yaml_header:
            yaml_header = get_dict_yaml_header("xxx", "1.0", "词库名称", "词库描述")
        fw.write(yaml_header)
        fw.write(str_result)
    print("处理完毕，结果文件:", yaml_file_out)
