#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-10-11 11:32:43
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
import itertools
from collections import defaultdict
from func_lib import load_char_code

class SchemaFlypyPro:
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, map_shengmu: dict, map_yunmu: dict):
        print("初始化中...")
        # 1.双拼方案映射表
        self.map_shengmu = map_shengmu
        self.map_yunmu = map_yunmu
        self.dir_in = dir_in
        # 2.取两码形码作为辅助码
        self.dict_char_codes = load_char_code(os.path.join(self.dir_in, fname_full)) # 单字全码, 加参数len=2则是取前两码
        # (a)分析每个汉字的字根数
        file_chaifen = "material_yujoy/yujoy_chaifen_v3.6.0.dict.yaml"  # 卿云
        # file_chaifen = "material_yustar/yustar_chaifen_v3.6.0.dict.yaml"  # 星陈
        dict_char_len = {}  # 每个汉字的字根数
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
        # (b)提取首末字根的大码(单根字则补小码)
        self.dict_char_codes_sup = defaultdict(set)
        for char, codes in self.dict_char_codes.items():
            for code in codes:
                if len(code) in (2, 3):
                    self.dict_char_codes_sup[char].add(code[:2])
                elif dict_char_len.get(char,4) == 3:  # 4码，三根字的情况
                    self.dict_char_codes_sup[char].add(code[0]+code[2])
                else:  # 4码，四根以上字的情况
                    self.dict_char_codes_sup[char].add(code[0]+code[-1])
        # 3.输出
        self.dir_out = dir_out
        if not os.path.exists(self.dir_out):
            os.makedirs(self.dir_out)

    def build(self):
        # 1.白霜(frost)词库
        dir_ciku = "material_common/cn_dicts"  # tencent.dict.yaml
        files_in = ['8105.dict.yaml', '41448.dict.yaml', 'base.dict.yaml', 'ext.dict.yaml', 'others.dict.yaml']
        # (待生成) 形码整句版词库
        files_out = ['8105.dict.yaml', '41448.dict.yaml', 'base.dict.yaml', 'ext.dict.yaml', 'others.dict.yaml']
        # files_out = ['chars.dict.yaml', 'chars_ext.dict.yaml', 'words.dict.yaml', 'words_ext.dict.yaml', 'words_ext2.dict.yaml']
        
        # 2.开始处理
        for i in range(len(files_in)):
            file_in = os.path.join(dir_ciku, files_in[i])
            file_out = os.path.join(self.dir_out, files_out[i])
            print("开始处理", file_in)
            self.convert_dict_yaml_file(file_in, file_out)

    def convert_dict_yaml_file(self, file_in: str, file_out: str, filter_flag: bool=False):
        str_result = ""
        with open(file_in, 'r', encoding='utf-8') as fr:
            # 按行处理
            for line in fr:
                # 1.解析(全拼)编码行
                if '\t' not in line or line.startswith("#"):
                    str_result += line  # 非编码行直接拷贝
                    continue
                line = line.strip()
                freq = "0"
                if len(line.split('\t')) == 3:
                    word, str_pinyin, freq = line.split('\t')
                else:
                    word, str_pinyin = line.split('\t')
                
                # 2.处理拼音部分
                lst_pinyin = str_pinyin.split(" ")
                lst_double_pinyin = []
                for pinyin in lst_pinyin:
                    if len(pinyin) == 2:  # 包含 ya, en, er, ai, ... 等情况
                        double_pinyin = pinyin
                    elif len(pinyin) == 1:  # 包含 a, o, e 情况
                        double_pinyin = pinyin * 2
                    else:
                        # 1.解析全拼的声母、韵母
                        shengmu = pinyin[0] # 声母部分
                        yunmu = pinyin[1:]  # 韵母部分
                        # 对特殊情况做修正
                        if pinyin[0] in ('a','o','e'):  # (三字母)零声母, 包含 ang, eng 情况
                            yunmu = pinyin
                        elif pinyin[1] == "h":  # 翘舌音, 包含 zh.., ch.., sh.. 情况
                            shengmu = pinyin[:2]
                            yunmu = pinyin[2:]

                        # 2.映射得到双拼的声母、韵母两键
                        double_shengmu = self.map_shengmu.get(shengmu, shengmu)  # 双拼第一码(声母)
                        double_yummu = self.map_yunmu.get(yunmu, yunmu)  # 双拼第二码(韵母)
                        if len(double_shengmu) != 1 or len(double_yummu) != 1:
                            print("该拼音有误(双拼将使用默认码ak)：", pinyin)
                            double_pinyin = "ak"
                        else:
                            double_pinyin = double_shengmu + double_yummu
                    lst_double_pinyin.append(double_pinyin)

                # 3.整合形成新的(双拼+形)编码行
                # (a)拼接成完整编码(双拼+形)
                lst_codes = []
                punc_pat = re.compile(r"[，。《〈«‹》〉»›？；：‘’“”、～！……·（）－—「【〔［」】〕］『〖｛』〗｝]")
                word_pure = punc_pat.sub("", word)
                if len(word_pure) == len(lst_double_pinyin):
                    # 获取所有可能的形码编码组合
                    lst_set_sup = []
                    for char in word_pure:
                        lst_set_sup.append(self.dict_char_codes_sup.get(char, {"ak"}))
                    # 按每个组合情况分别拼接
                    for pair in itertools.product(*lst_set_sup):
                        codes = []
                        for i in range(len(lst_double_pinyin)):
                            codes.append(lst_double_pinyin[i] + pair[i] + '0')
                        lst_codes.append(codes)
                    # (b)匹配词频
                    for codes in lst_codes:
                        if filter_flag and "41448" in file_in:
                            str_result += f"[超集字]{word}[超]\t{' '.join(codes)}\t{freq}\n"
                        else:
                            str_result += f"{word}\t{' '.join(codes)}\t{freq}\n"
                else:
                    print("拼音数和汉字数不相等，已跳过该行：", line)
        # 保存结果
        with open(file_out, 'w', encoding='utf-8') as fw:
            fw.write(str_result)


if __name__ == '__main__':
    import time
    start = time.perf_counter()

    map_shengmu = { "zh": "v", "ch": "i", "sh": "u" }
    map_yunmu = {
        'iu': 'q',
        'ei': 'w',
        'uan':'r', 'van':'r',
        'ue': 't', 've': 't',
        'un': 'y', 'vn': 'y',
        'uo': 'o',
        'ie': 'p',
        'iong': 's', 'ong': 's',
        'ai': 'd',
        'en': 'f',
        'eng': 'g',
        'ang': 'h',
        'an': 'j',
        'ing': 'k', 'uai': 'k',
        'iang': 'l', 'uang': 'l',
        'ou': 'z',
        'ia': 'x', 'ua': 'x',
        'ao': 'c',
        'ui': 'v',
        'in': 'b',
        'iao': 'n',
        'ian': 'm',
    }
    # 卿云
    myschema = SchemaFlypyPro(
        "material_yujoy",
        "yujoy.full.dict_v3.6.0.yaml",
        "schema_flypy_pro/dicts_flypy_pro",
        map_shengmu,
        map_yunmu
    )
    # # 星陈
    # myschema = SchemaFlypyPro(
    #     "material_yustar",
    #     "yustar.full.dict_v3.6.0.yaml",
    #     "schema_flypy_pro2/dicts_flypy_pro",
    #     map_shengmu,
    #     map_yunmu
    # )
    myschema.build()

    print("\nRuntime:", time.perf_counter() - start)
