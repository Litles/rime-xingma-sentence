#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-07 00:42:52
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
from schema_yujoy_fluid import SchemaYujoyFluid
from func_lib import (
    load_word_freq,
    load_char_code,
    get_charset
)

class SchemaYustarFluid(SchemaYujoyFluid):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        # 输入
        print("初始化中...")
        self.dir_in = dir_in
        self.dict_char_codes = load_char_code(os.path.join(self.dir_in, fname_full), full_only=False)  # 单字全码码表(大概100,000字)
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

        # 1.调整字根字全码为两码
        n_altered = 0
        for char, codes in self.dict_char_codes.items():
            if len(codes) > 1:  # 字根字只保留两码的编码
                self.dict_char_codes[char] = set(code for code in codes if len(code) == 2)
                n_altered += 1
        print("已剔除三码字(实为字根)个数:", n_altered)
        # 2.去除回头码
        n_altered = 0
        dict_char_len = {}  # 每个汉字的字根数
        file_chaifen = os.path.join(self.dir_in, "yustar_chaifen_v3.6.0.dict.yaml")
        with open(file_chaifen, 'r', encoding='utf-8') as fr:
            pat = re.compile(r"({[^\}]+})")
            for line in fr:
                line = line.strip()
                if (not line.startswith("#")) and ("\t" in line):
                    char, others = line.split("\t", 1)
                    chaifen = others.lstrip("[").split(",", 1)[0]
                    if len(chaifen) > 0:
                        chaifen = pat.sub("字", chaifen)
                        dict_char_len[char] = len(chaifen)
        dict_char_code_tmp = {}  # 用于收集两根字
        for char, codes in self.dict_char_codes.items():
            if dict_char_len[char] == 2:  # 两根字
                for code in self.dict_char_codes[char]:
                    if len(code) == 4: # 检查是否编码长度为 4
                        dict_char_code_tmp[char] = code
                    else:
                        print("[异常]原两根字编码长度不为4：", char, codes)
        for char, code in dict_char_code_tmp.items():
            self.dict_char_codes[char].remove(code)
            self.dict_char_codes[char].add(code[:3])
            n_altered += 1
        print("已调整两根字不回头的个数:", n_altered)

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    # myschema = SchemaYustarFluid(
    #     "material_yustar",
    #     "yustar.full.dict_v3.6.0.yaml",
    #     "schema_yustar_fluid/dicts_yustar_fluid",
    #     "星陈",
    #     "2.3"
    # )
    # myschema.build()
    myschema = SchemaYustarFluid(
        "material_yustar",
        "yustar.full.dict_v3.6.0.yaml",
        "schema_yustar_fluid/dicts_yustar_fluid_a",
        "星陈",
        "2.3"
    )
    myschema.build("A")  # a版
    myschema.generate_other_dicts()
    print("\nRuntime:", time.perf_counter() - start)
