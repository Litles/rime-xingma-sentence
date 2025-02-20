#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-16 18:39:12
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

from collections import defaultdict
import os
import re
import itertools
from func_lib import get_charset

def encode(word: str, dict_char_codes: dict) -> set:
    set_codes = set()
    if len(word) == 1:  # 单字
        return dict_char_codes[word]
    elif len(word) == 2:  # 二字词
        char1_len2_codes = set(code[:2] for code in dict_char_codes[word[0]])  # 第一字的前两码Aa
        char2_len2_codes = set(code[:2] for code in dict_char_codes[word[1]])  # 第二个字的前两码Bb
        for pair in itertools.product(char1_len2_codes, char2_len2_codes):
            set_codes.add("".join(pair))
    elif len(word) == 3:  # 三字词
        char1_len1_codes = set(code[0] for code in dict_char_codes[word[0]])  # 第一字的首码A
        char2_len1_codes = set(code[0] for code in dict_char_codes[word[1]])  # 第二个字的首码B
        char3_len2_codes = set(code[:2] for code in dict_char_codes[word[2]])  # 第三个字的前两码Cc
        for pair in itertools.product(char1_len1_codes, char2_len1_codes, char3_len2_codes):
            set_codes.add("".join(pair))
    elif len(word) > 3:  # 四字词及以上
        char1_len1_codes = set(code[0] for code in dict_char_codes[word[0]])  # 第一字的首码A
        char2_len1_codes = set(code[0] for code in dict_char_codes[word[1]])  # 第二个字的首码B
        char3_len1_codes = set(code[0] for code in dict_char_codes[word[2]])  # 第三个字的首码C
        charLast_len1_codes = set(code[0] for code in dict_char_codes[word[-1]])  # 最后一个字的首码Z
        for pair in itertools.product(char1_len1_codes, char2_len1_codes, char3_len1_codes, charLast_len1_codes):
            set_codes.add("".join(pair))
    return set_codes

def get_encoded_words(file_in: str, dict_char_codes: dict, len_min: int=-1, filter_flag: bool=True) -> list:
    list_word_code = []
    charset = set()
    if filter_flag:
        charset = get_charset("字符集/G标/GB18030汉字集_无兼容汉字.txt", "字符集/G标_通规/通规（8105字）.txt")
        charset.add("〇")  # 该字被收录到符号区，但应作为汉字使用，故加之
    punc_pat = re.compile(r"[，。《〈«‹》〉»›？；：‘’“”、～！……·（）－—「【〔［」】〕］『〖｛』〗｝]")
    with open(file_in, 'r', encoding='utf-8') as fr:
        for line in fr:
            word = line.strip()
            if word:
                word_pure = punc_pat.sub("", word)
                if not word_pure:
                    continue
                if filter_flag and (not set(word_pure).issubset(charset)):
                    print("该词中包含未能识别的字符，已跳过：", word)
                    with open('encode_error_words.txt', 'a', encoding='utf-8') as fa:
                        fa.write(word + "\n")
                elif len_min == -1:
                    for code in encode(word_pure, dict_char_codes):
                        list_word_code.append({"word": word, "code": code})
                else:
                    if len(word_pure) >= len_min:
                        for code in encode(word_pure, dict_char_codes):
                            list_word_code.append({"word": word, "code": code})
    return list_word_code


def get_encoded_words_en(file_in: str) -> list:
    """ 只支持4个字母以上的词组 """
    list_word_code = []
    letters = "zyxwvutsrqponmlkjihgfedcbaABCDEFGHIJKLMNOPQRSTUVWXYZ"
    charset = set(letters+" -+:/0123456789.")
    punc_pat = re.compile(r"[\-+:/0123456789\.]")
    with open(file_in, 'r', encoding='utf-8') as fr:
        for line in fr:
            word = line.strip()
            if word:
                word_pure = punc_pat.sub("", word)
                if not word_pure:
                    continue
                if (not set(word_pure).issubset(charset)) or len(word_pure.replace(" ", "")) < 3:
                    print("该词中包含未能识别的字符或不足3个字母，已跳过：", word)
                    with open('encode_error_words.txt', 'a', encoding='utf-8') as fa:
                        fa.write(word + "\n")
                elif len(word_pure) == 3:
                    list_word_code.append({"word": word, "code": word_pure.lower()+"v"})
                else: # len >= 4
                    if " " in word_pure:
                        c_end = word_pure.rsplit(" ", 1)[-1][0].lower()
                        list_word_code.append({"word": word, "code": word_pure[:3].lower()+c_end})
                    else:
                        list_word_code.append({"word": word, "code": word_pure[:3].lower()+word_pure[-1].lower()})
    return list_word_code

def sort_mabiao_file(file_in: str, dict_word_freq: dict) -> None:
    """生成排序后的码表(忽略注释行)
    
    Args:
        file_in (str): 待排序的码表, 可以带编码也可以不带(纯字词清单)
        dict_word_freq (dict): 词频表
    """
    list_words = []
    with open(file_in, 'r', encoding='utf-8') as fr:
        for line in fr:
            if (not line.startswith("#")) and ("\t" in line):
                word = line.split("\t", 1)[0]
                list_words.append({"word": word, "line": line})
            elif (not line.startswith("#")) and line.strip():  # 可用于处理(无编码的)纯字词清单
                word = line.split(None, 1)[0]
                list_words.append({"word": word, "line": line})
    list_words.sort(key=lambda d: dict_word_freq.get(d["word"], 0), reverse=True)
    root, ext= os.path.splitext(file_in)
    with open(root+"_sorted"+ext, 'w', encoding='utf-8') as fw:
        for d in list_words:
            fw.write(d["line"])

def split_long_words(file_in: str) -> None:
    """分割长词，比如把 "满招损，谦受益" 分割成:
    "满招损<TAB>满招损，谦受益" 和 "谦受益<TAB>满招损，谦受益"
    
    Args:
        file_in (str): 长词txt文件，一行一个词
    """
    punc_pat = re.compile(r"[，。《〈«‹》〉»›？；：‘’“”、～！……·（）－—「【〔［」】〕］『〖｛』〗｝]")
    root, ext= os.path.splitext(file_in)
    with (
        open(file_in, 'r', encoding='utf-8') as fr,
        open(root+"_pieces"+ext, 'w', encoding='utf-8') as fw,
    ):
        for line in fr:
            word = line.strip()
            if word:
                lst = punc_pat.split(word)
                if len(lst) > 1:
                    for item in lst:
                        if len(item) > 1:
                            fw.write(f"{item}\t{word}\n")
