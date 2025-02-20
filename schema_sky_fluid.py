#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-10-06 00:17:06
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
from collections import defaultdict
from schema_yujoy_fluid import SchemaYujoyFluid
from func_lib import (
    load_word_freq,
    get_charset
)

class SchemaSkyFluid(SchemaYujoyFluid):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        # 输入
        print("初始化中...")
        self.dir_in = dir_in
        # self.dict_char_codes = load_char_code(os.path.join(self.dir_in, fname_full))  # 单字全码码表(大概100,000字)
        self.file_quick1 = os.path.join(self.dir_in,"quick_chars.txt")  # 指定一二简(字符)
        self.file_quick2 = os.path.join(self.dir_in,"quick_others.txt")  # 指定二三简(其它)
        self.file_quick3 = os.path.join(self.dir_in,"quick_special.txt")  # 指定二三简(其它)
        self.list_char_code = []  # 将以包含 "char","code","freq" 三个键的 dict 为元素
        self.set_qc_char = set()  # 记录所设的简字
        # 子集和词频相关数据
        self.dict_char_freq = load_word_freq("字词频/知频_字频.txt")  # 字频(词频对于曰常聊天优于"25亿")
        self.dict_word_freq = load_word_freq("字词频/知频_字词频.txt")  # 知频_字词频.txt (里面的字符都在GBK汉字+[a-z|A-Z|\d]范围内, 但只包含7471个通规字)
        self.set_base = get_charset("字符集/G标/GB18030汉字集_无兼容汉字.txt", "字符集/G标_通规/通规（8105字）.txt")
        self.set_base.add("〇")  # 该字被收录到符号区，但应作为汉字使用，故加之
        # 输出
        self.dir_out = dir_out
        self.sname = sname
        self.version = version
        if not os.path.exists(self.dir_out):
            os.makedirs(self.dir_out)

        # 0.加载拆分表(从中提取单字全码码表)
        pat = re.compile(r"({[^\}]+})")
        self.dict_char_codes = defaultdict(set)
        set_char_len2 = set()
        set_char_len3 = set()
        with open(os.path.join(self.dir_in, fname_full), 'r', encoding='utf-8') as fr:
            for line in fr:
                char, chaifen = line.split("\t")
                chaifen = chaifen.split(";")[0].lstrip("〔")
                if "{" in chaifen:
                    chaifen = pat.sub("字", chaifen)
                for cf in chaifen.split(","):  # 可能有兼容拆分
                    code, chai = cf.split("·")
                    if len(chai) == 1:
                        self.dict_char_codes[char].add(code[:2])  # 两码全码
                        set_char_len2.add(char)
                    elif len(chai) == 2:
                        self.dict_char_codes[char].add(code[:3])  # 去回头码
                        set_char_len3.add(char)
                    else:
                        self.dict_char_codes[char].add(code)
        # print(self.dict_char_codes["槑"], self.dict_char_codes["㒫"], self.dict_char_codes["𗢨"])
        print("共取得汉字总数:", len(self.dict_char_codes))
        print("其中两码字、三码字个数:", len(set_char_len2), len(set_char_len3))

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    # myschema = SchemaSkyFluid(
    #     "material_sky",
    #     "sky_char_chaifen.txt",
    #     "schema_sky_fluid/dicts_sky_fluid",
    #     "天码",
    #     "2.3"
    # )
    # myschema.build()
    myschema = SchemaSkyFluid(
        "material_sky",
        "sky_char_chaifen.txt",
        "schema_sky_fluid/dicts_sky_fluid_a",
        "天码",
        "2.3"
    )
    myschema.build("A")  # A版
    print("\nRuntime:", time.perf_counter() - start)
"""
对官方天码的调整

* 字根字一律只取两码(A版补小码成三码)
* 原三码的双根字一律只取三码，即无回头码/补"v"
"""
