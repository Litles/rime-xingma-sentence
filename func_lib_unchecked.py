#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-15 23:31:59
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
import statistics
from collections import defaultdict
from func_lib import (
    generate_dict_file_with_freq, load_word_freq,
    load_char_code, compute_char_chongma,
    get_charset, combine_code_and_freq
)

def get_char_freq_with_csFlag(dict_char_freq: dict) -> list:
    """给字频表添加字集标记
    
    Args:
        dict_char_freq (dict): 字频表
    
    Returns:
        list: 有字集标记的字频表
    """
    list_char_freq = []
    # 1.load charset files
    dict_charsets = {}
    cs_all = set()
    files = {
        "tg1": "字符集/G标_通规/通规一级（3500字）.txt",
        "tg2": "字符集/G标_通规/通规二级（3000字）.txt",
        "tg3": "字符集/G标_通规/通规三级（1605字）.txt",
        "gb2312": "字符集/G标/GB2312汉字集.txt"
    }
    for csName in files:
        with open(files[csName], 'r', encoding='utf-8') as fr:
            dict_charsets[csName] = set(fr.read().replace("\r", "").replace("\n", ""))
            cs_all |= dict_charsets[csName]
    # 2.tag charsets to char_freq
    for char in cs_all:
        flag_tg1, flag_tg2, flag_tg3, flag_gb2312 = 0, 0, 0, 0
        if char in dict_charsets["tg1"]:
            flag_tg1 = 1
        if char in dict_charsets["tg2"]:
            flag_tg2 = 1
        if char in dict_charsets["tg3"]:
            flag_tg3 = 1
        if char in dict_charsets["gb2312"]:
            flag_gb2312 = 1
        list_char_freq.append({
            "char": char,
            "freq": dict_char_freq.get(char, 0),
            "tg1": flag_tg1,
            "tg2": flag_tg2,
            "tg3": flag_tg3,
            "gb2312": flag_gb2312,
            "all": 1
        })

    # 3.sort and statistics
    list_char_freq.sort(key=lambda d: d["freq"], reverse=True)
    for i in range(len(list_char_freq)):
        list_char_freq[i]["rank"] = i+1
    # print("tg1无频字:", [d["char"] for d in list_char_freq if d["tg1"] == 1 and d["freq"] == 0])
    print("tg1低频字(排在6000后):", [d["char"] for d in list_char_freq if d["tg1"] == 1 and d["rank"] > 6000])
    print("tg3高频字(排在前2500):", [d["char"] for d in list_char_freq if d["tg3"] == 1 and d["rank"] < 2500])
    print("字集", "总字数", "最高排名", "上分位", "中位", "下分位", "最低排名")
    for csName in dict_charsets:
        lst = [d["rank"] for d in list_char_freq if d[csName]==1]
        print(
            csName,
            sum(d[csName] for d in list_char_freq),
            min(lst),
            int(statistics.quantiles(lst, n=4)[0]),
            int(statistics.median(lst)),
            int(statistics.quantiles(lst, n=4)[2]),
            max(lst)
        )

    # 4.write to file
    # with open('out.csv', 'w', encoding='utf-8') as fw:
    #     cnames = list(list_char_freq[0].keys())
    #     writer = csv.DictWriter(fw, fieldnames=cnames, delimiter='\t', lineterminator='\n')
    #     writer.writeheader()
    #     writer.writerows(list_char_freq)
    return list_char_freq


def compare_two_freq_table():
    # freq_table to compare
    file_freq1 = "字词频/知频_字频.txt"
    file_freq2 = "字词频/25亿字语料汉字字频表(14975字).txt"
    dict_char_freq1 = load_word_freq(file_freq1)
    dict_char_freq2 = load_word_freq(file_freq2)
    # charset
    charset = get_charset("字符集/G标_通规/通规（8105字）.txt", "字符集/G标/GB2312汉字集.txt")
    dict_char_codes = load_char_code("yujoy.full.dict_v3.6.0_rc5.yaml")  # 单字全码码表(大概100,000字)
    list_char_freq1 = combine_code_and_freq(dict_char_codes, dict_char_freq1, charset)
    list_char_freq2 = combine_code_and_freq(dict_char_codes, dict_char_freq2, charset)
    for d in list_char_freq1:
        if len(d["code"]) >= 3:
            d["code"] = d["code"][:3]
    for d in list_char_freq2:
        if len(d["code"]) >= 3:
            d["code"] = d["code"][:3]
    # assert len(list_char_freq1) == len(list_char_freq2)
    list_char_freq1.sort(key=lambda d: d["freq"], reverse=True)
    list_char_freq2.sort(key=lambda d: d["freq"], reverse=True)
    dict_code_chars1 = compute_char_chongma(list_char_freq1, True, charset)
    dict_code_chars2 = compute_char_chongma(list_char_freq2, False, charset)
    # assert len(dict_code_chars1) == len(dict_code_chars2)
    # print(len(dict_code_chars1))
    # for i in range(len(dict_code_chars1)):
    # for code, chars in dict_code_chars1.items():
    #     if code == "ls":
    #         print(chars)
    n_diff = 0
    with open('out.txt', 'w', encoding='utf-8') as fw:
        fw.write("编码\t知频\t语频\n")
        for code, chars in dict_code_chars1.items():
            if chars[:2] != dict_code_chars2[code][:2]:
                n_diff += 1
                # if n_diff == 1:
                #     print("知频", chars)
                #     print("语频", dict_code_chars2[code])
                fw.write(f"{code}\t{chars}\t{dict_code_chars2[code]}\n")
        print(n_diff)


def get_sample_chars_of_root():
    # char freq
    list_char_freq = []
    set_chars_with_freq = set()
    for char, freq in load_word_freq("字词频/知频_字频.txt").items():
        list_char_freq.append({"char": char, "freq": freq})
        set_chars_with_freq.add(char)
    list_char_freq.sort(key=lambda d: d["freq"], reverse=True)
    # chars without freq
    set_base = get_charset("字符集/G标/GB18030汉字集_无兼容汉字.txt", "字符集/G标_通规/通规（8105字）.txt")
    for char in set_base - set_chars_with_freq:
        list_char_freq.append({"char": char, "freq": 0})
        set_chars_with_freq.add(char)
    dict_char_codes = load_char_code(os.path.join("yujoy","char_code.txt"))
    for char in set(dict_char_codes.keys()) - set_chars_with_freq:
        list_char_freq.append({"char": char, "freq": 0})
    # root and chars
    dict_char_roots = defaultdict(set)
    with open('yujoy/yujoy_chaifen.dict.yaml', 'r', encoding='utf-8') as fr:
        pat = re.compile(r"({[^\}]+})")
        for line in fr:
            line = line.strip()
            if (not line.startswith("#")) and ("\t" in line):
                char, others = line.split("\t", 1)
                chaifen = others.lstrip("[").split(",", 1)[0]
                for root in pat.findall(chaifen):
                    dict_char_roots[root].add(char)
                for root in pat.sub("", chaifen):
                    dict_char_roots[root].add(char)
    # get root-chars list
    with open('out.txt', 'w', encoding='utf-8') as fw:
        for root, set_chars in dict_char_roots.items():
            chars = ""
            for d in list_char_freq:
                if len(chars) < 10 and d["char"] in set_chars:
                    chars += d["char"]
                elif len(chars) >= 10:
                    break
            fw.write(f"{root}\t{chars}\n")

def match_author():
    dict_poem_author = {}
    with open("词典/唐诗宋词鉴赏合集_comment.txt", 'r', encoding='utf-8') as fr:
        for line in fr:
            author, poem = line.strip().split("\t")
            dict_poem_author[poem] = author
    punc_pat = re.compile(r"[，。《〈«‹》〉»›？；：‘’“”、～！……·（）－—「【〔［」】〕］『〖｛』〗｝]")
    with (
        open("词典/唐诗宋词鉴赏合集_ext.txt", 'r', encoding='utf-8') as fr,
        open("词典/唐诗宋词鉴赏合集_ext_match.txt", 'w', encoding='utf-8') as fw,
    ):
        for line in fr:
            word = line.strip()
            if word:
                lst = punc_pat.split(word)
                lst_pure = [s for s in lst if len(s) > 1]
                for poem in dict_poem_author:
                    res = sum(1 for item in lst_pure if item in poem)
                    if res == len(lst_pure):
                        fw.write(f"{word}\t{dict_poem_author[poem]}\n")
                        break

def analyse_len2_supplement_choice():
    # 分析两码字补什么字母(成三码)好
    dict_char_codes = load_char_code(os.path.join("material_yujoy","yujoy.full.dict_v3.6.0.yaml"))
    dict_char_freq = load_word_freq("字词频/知频_字频.txt")
    set_base = get_charset("字符集/G标/GB18030汉字集_无兼容汉字.txt", "字符集/G标_通规/通规（8105字）.txt")
    list_char_code = combine_code_and_freq(dict_char_codes, dict_char_freq, set_base)
    list_char_code.sort(key=lambda d: d["freq"], reverse=True)
    dict_code_chars_len2 = defaultdict(str)
    list_char_code_len3_len4 = []
    for d in list_char_code:
        if len(d["code"]) == 2:
            dict_code_chars_len2[d["code"]+"z"] += d["char"]  # add 'z' suffix
        elif len(d["code"]) >= 3:
            list_char_code_len3_len4.append(d)
    bar = list_char_code[7999]["freq"]  # analyse range
    with open('out_z.txt', 'w', encoding='utf-8') as fw:
        for code, chars in dict_code_chars_len2.items():
            s = ""
            for d in list_char_code_len3_len4:
                if d["freq"] >= bar and d["code"][:3] == code:
                    s += d["char"]
            fw.write(f"{code}\t{chars}\t{s}\n")
