#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-07 00:42:52
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 2.4

import os
import re
from collections import defaultdict
import itertools
from mabiao_utils import get_encoded_words, get_encoded_words_en
from func_lib import (
    load_word_freq,
    load_char_code,
    compute_char_chongma,
    adjust_zhi_char_freq,
    get_dict_yaml_header,
    get_charset,
    combine_code_and_freq,
    generate_dict_yaml_ciku
)

class SchemaYujoyFluid:
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        # 输入
        print("初始化中...")
        self.dir_in = dir_in
        self.source_file = fname_full
        self.dict_char_codes = load_char_code(os.path.join(self.dir_in, fname_full))  # 单字全码码表(大概100,000字)
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

    def build(self, za_flag: str="", yujoy_flag: bool=False) -> None:
        # 0.准备字频表
        adjust_zhi_char_freq(self.dict_char_freq) # 微调原字频
        if za_flag == "" and yujoy_flag:
            # (仅适用于空格版卿云)由于首选有设简，调整次选为首选
            self.dict_char_freq["哥"], self.dict_char_freq["歌"] = self.dict_char_freq["歌"], self.dict_char_freq["哥"]
            self.dict_char_freq["吗"], self.dict_char_freq["嗯"] = self.dict_char_freq["嗯"], self.dict_char_freq["吗"]

        # 1.匹配基本字集所有汉字的编码
        self.list_char_code = combine_code_and_freq(self.dict_char_codes, self.dict_char_freq, self.set_base)
        n_chars = len(self.set_base)
        if len(self.list_char_code) == n_chars:
            print(f"成功匹配基本集全部 {n_chars} 字的编码")  # 27,711
        # (z/a版)修改两码全码字(即字根)成三码全码
        if za_flag == "Z":
            for d in self.list_char_code:
                if len(d["code"]) == 2:
                    d["code"] += "z"
        elif za_flag == "A":
            for d in self.list_char_code:
                if len(d["code"]) == 2:
                    d["code"] += d["code"][1]
        elif za_flag == "" and yujoy_flag:
            # (仅适用于空格版卿云) 为腾出空间设简，先用占位符将原二码字往后挤：钅(vj),風(sf),彡(ws),弋(ki),匸(tf),瓦(nw),廴(gi),丌(oj),卩(ej),甫(af)
            self.list_char_code.append({"char": "∎", "code": "vj", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "sf", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "ws", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "ki", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "tf", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "nw", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "gi", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "oj", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "ej", "freq": 99999})
            self.list_char_code.append({"char": "∎", "code": "af", "freq": 99999})

        # 2.部分单字额外设“一二三简”, 全码多重设“标记”(即[2-9]重)，三连击设兼容码
        # 以下两个操作都会修改 self.list_char_code
        self.set_quick_code(za_flag, yujoy_flag)   # 额外设“一二三简”(若是z/a版则不设一二简)
        self.list_char_code.sort(key=lambda d: d["freq"], reverse=True)
        freq_var = 400_000
        for dct in self.list_char_code:
            dct["freq"] = freq_var
            freq_var -= 1
        self.set_choice_mark()  # 全码多重设“标记”(即[2-9]重)

        # 3.获取扩展字集, 生成单字码表(单字yaml码表文件)
        list_char_code_ext = []
        for char, code in self.dict_char_codes.items():
            if char not in self.set_base:
                str_code = list(code)[0]
                if len(str_code) == 2 and za_flag == "Z":  # (z版)两码字补充z
                    str_code = (str_code+"z1").ljust(5, "=")
                elif len(str_code) == 2 and za_flag == "A":  # (a版)两码字补充小码
                    str_code = (str_code+str_code[1]+"1").ljust(5, "=")
                else:
                    str_code = (str_code+"1").ljust(5, "=")
                list_char_code_ext.append({
                    "char": char,
                    "code": str_code,
                    "freq": 0
                })
        list_char_code_ext.sort(key=lambda d: d["char"])
        print("\n---> 开始生成yaml词库文件...")
        if za_flag == "" and yujoy_flag:
            # (仅适用于空格版卿云) 保留原被挤的二码字首选全码
            self.list_char_code.append({"char": "钅", "code": "vj1==", "freq": 1})
            self.list_char_code.append({"char": "風", "code": "sf1==", "freq": 1})
            self.list_char_code.append({"char": "彡", "code": "ws1==", "freq": 1})
            self.list_char_code.append({"char": "弋", "code": "ki1==", "freq": 1})
            self.list_char_code.append({"char": "匸", "code": "tf1==", "freq": 1})
            self.list_char_code.append({"char": "瓦", "code": "nw1==", "freq": 1})
            self.list_char_code.append({"char": "廴", "code": "gi1==", "freq": 1})
            self.list_char_code.append({"char": "丌", "code": "oj1==", "freq": 1})
            self.list_char_code.append({"char": "卩", "code": "ej1==", "freq": 1})
            self.list_char_code.append({"char": "甫", "code": "af1==", "freq": 1})
        self.generate_dict_yaml_dz(list_char_code_ext)

        # 4.生成简词(二三简)词库
        if za_flag:  # z/a版只设三简
            dict_name = "words_quick"
            file_out = os.path.join(self.dir_out, dict_name+".dict.yaml")
            with (
                open(self.file_quick2, 'r', encoding='utf-8') as fr,
                open(file_out, 'w', encoding='utf-8') as fw
            ):
                yaml_header = get_dict_yaml_header(dict_name, self.version, f"三码{self.sname}·简码词", "包含汉字词符号和字母数字")
                fw.write(yaml_header)
                # 加载预设(三简词), 三简不检查
                for line in fr:
                    word, code = line.strip().split("\t")
                    if len(code) == 3 and code.startswith("z"):
                        fw.write(f"{word}\t{code.ljust(5,'=')}\t1\n")
                    elif len(code) == 3:
                        fw.write(f"{word}\t{code.ljust(5,'=')}\t999999\n")
            print("处理完毕，结果文件:", file_out)
        else:
            self.generate_dict_yaml_jianci()
        # 5.生成特殊(英文数字)词库
        dict_name = "words_special"
        file_out = os.path.join(self.dir_out, dict_name+".dict.yaml")
        with (
            open(self.file_quick3, 'r', encoding='utf-8') as fr,
            open(file_out, 'w', encoding='utf-8') as fw
        ):
            yaml_header = get_dict_yaml_header(dict_name, self.version, f"三码{self.sname}·特殊词", "字母、数字和小数点")
            fw.write(yaml_header)
            for line in fr:
                word, code = line.strip().split("\t")
                fw.write(f"{word}\t{code.ljust(5,'=')}\t0\n")
        print("处理完毕，结果文件:", file_out)

        # 6.生成词库(词库yaml码表文件)
        # (0)准备全部单字编码映射(一字可能有多个码)
        dict_char_codes_new = defaultdict(set)  # 将包含简码在内
        for d in itertools.chain(self.list_char_code, list_char_code_ext):
            dict_char_codes_new[d["char"]].add(d["code"])
        # (1)生成基础词库
        dir_in = "material_common/cn_dicts"
        dct = {
            "base.dict.yaml": "words",
            "ext.dict.yaml": "words_ext",
            "others.dict.yaml": "words_ext2"
        }
        list_word_wcode = []  # 用于收集满足条件的二字词条目，用于生成选重词库
        words_done = set()
        for fname in os.listdir(dir_in):
            if fname in dct:
                dict_meta = {
                    "name": dct[fname],
                    "version": self.version,
                    "name_zh": f"三码{self.sname}·词库",
                    "desc": "生成自白霜(frost)词库 " + fname
                }
                list_word_wcode_temp, words_done_temp = generate_dict_yaml_ciku(
                    os.path.join(dir_in, fname),
                    dict_char_codes_new,
                    self.dict_word_freq,
                    dict_meta,
                    self.dir_out,
                    words_done
                )
                list_word_wcode += list_word_wcode_temp
                words_done |= words_done_temp
        # (2)生成用户词库
        file_in = "material_common/words_user.txt"
        dict_meta = {
            "name": "words_user",
            "version": self.version,
            "name_zh": f"三码{self.sname}·用户词",
            "desc": "用于统一存放用户自定义生成的词"
        }
        list_word_wcode_temp, words_done_temp = generate_dict_yaml_ciku(
            file_in,
            dict_char_codes_new,
            self.dict_word_freq,
            dict_meta,
            self.dir_out,
            words_done
        )
        list_word_wcode += list_word_wcode_temp
        # (3)生成选重词库(z/a版不支持)
        if not za_flag:
            self.generate_dict_yaml_shift(list_word_wcode)
        else:
            self.generate_dict_yaml_shift_za()

    def generate_dict_yaml_shift_za(self):
        """ 只生成单字快捷兼容(四码字,非常规操作,仅为了方便) """
        yaml_header = get_dict_yaml_header("words_shift", self.version, f"三码{self.sname}·词组选重及取消组词", f"有重的(末字为全码首选字)二字词选重，及取消末字参与组词")
        file_out = os.path.join(self.dir_out, "words_shift.dict.yaml")
        with open(file_out, 'w', encoding='utf-8') as fw:
            fw.write(yaml_header)
            # (1) 单字部分(用于取消组词，即防止整句前面部分发生变化)
            # (为非常规)准备
            set_char_quick_len3 = set()  # 三简字
            set_code_len3 = set()  # 全码三码字(的编码)
            # (为常规)准备
            pat_quick_len3 = re.compile(r"^[a-z]{3}$")
            pat = re.compile(r"^[a-z]+\d$")
            for dct in self.list_char_code:
                code = dct["code"].rstrip("=")
                if pat.match(code):
                    # fw.write(f"{dct['char']}\t{code.ljust(6, "+")}\t0\n")
                    # 全码三码字
                    if len(code) == 4:
                        set_code_len3.add(code[:3])
                # 三简字
                elif pat_quick_len3.match(code):
                    set_char_quick_len3.add(dct["char"])
            # (2) 单字快捷兼容(四码字,非常规操作,仅为了方便)
            dict_code_chars = defaultdict(list)
            for dct in self.list_char_code:
                code = dct["code"].rstrip("=")
                # (符合条件的)四码全码字
                if len(code) == 5 and (code[:3] not in set_code_len3):
                    if dct["char"] in set_char_quick_len3:
                        # 设了简的依然排第一
                        dict_code_chars[code[:3]].append({"char":dct["char"], "rank":0})
                    else:
                        # 未设简的取原序
                        dict_code_chars[code[:3]].append({"char":dct["char"], "rank":int(code[-1])})
            # 排序
            n_quick = 0
            for lst in dict_code_chars.values():
                lst.sort(key=lambda d: d["rank"], reverse=False)  # 从低到高排
                n_quick += 1
            # 写入文件
            for code,lst in dict_code_chars.items():
                for i in range(min(len(lst),9)): # 最多取9个
                    fw.write(f"{lst[i]['char']}\t{code}{i+1}+=\t{9-i}\n")
        print("快捷兼容组数:", n_quick)
        print("已生成文件", file_out)

    def generate_dict_yaml_shift(self, list_word_wcode):
        list_word_wcode.sort(key=lambda d: d["freq"], reverse=True)
        # 1.得到重码组
        dict_char_item = defaultdict(list)
        pat = re.compile(r"([a-z]{3})")
        for dct in list_word_wcode:
            mt = pat.search(dct["wcode"].split(" ", 1)[0])
            if mt:
                dict_char_item[mt.group(1)+dct["char"]].append({
                    "word": dct["word"],
                    "wcode": dct["wcode"],
                    "freq": dct["freq"]
                })
        # 2.处理，输出到文件
        yaml_header = get_dict_yaml_header("words_shift", self.version, f"三码{self.sname}·词组选重及取消组词", f"有重的(末字为全码首选字)二字词选重，及取消末字参与组词")
        file_out = os.path.join(self.dir_out, "words_shift.dict.yaml")
        n_all = 0
        n_above4 = 0
        with open(file_out, 'w', encoding='utf-8') as fw:
            fw.write(yaml_header)
            # (1) 词组部分(用于词组选重)
            for lst in dict_char_item.values():
                if len(lst) > 1:
                    n_all += 1
                    if len(lst) > 4:
                        n_above4 += 1
                    for i in range(len(lst)):
                        if i == 0:
                            fw.write(f"{lst[i]['word']}\t{lst[i]['wcode']}\t{lst[i]['freq']+1}\n")  # 词频加一确保是首选(Rime有去重机制，重复了没关系)
                        else:
                            code1, code2 = lst[i]['wcode'].split(" ", 1)
                            for c in code2.split(","):
                                if c.endswith("1==="):
                                    wc = c[:1] + str(min(i+1,9)) + "++++"
                                    fw.write(f"{lst[i]['word']}\t{code1+' '+wc}\t{str(max(10-i,0))}\n")
                                elif c.endswith("1=="):
                                    wc = c[:2] + str(min(i+1,9)) + "+++"
                                    fw.write(f"{lst[i]['word']}\t{code1+' '+wc}\t{str(max(10-i,0))}\n")
                                elif c.endswith("1="):
                                    wc = c[:3] + str(min(i+1,9)) + "++"
                                    fw.write(f"{lst[i]['word']}\t{code1+' '+wc}\t{str(max(10-i,0))}\n")
                                elif c.endswith("1"):
                                    wc = c[:4] + str(min(i+1,9)) + "+"
                                    fw.write(f"{lst[i]['word']}\t{code1+' '+wc}\t{str(max(10-i,0))}\n")
            # (2) 单字部分(用于取消组词，即防止整句前面部分发生变化)
            # (为非常规)准备
            set_char_quick_len3 = set()  # 三简字
            set_code_len3 = set()  # 全码三码字(的编码)
            # (为常规)准备
            pat_quick_len3 = re.compile(r"^[a-z]{3}$")
            pat = re.compile(r"^[a-z]+\d$")
            for dct in self.list_char_code:
                code = dct["code"].rstrip("=")
                if pat.match(code) and dct['char'] != "∎":
                    fw.write(f"{dct['char']}\t{code.ljust(6, "+")}\t0\n")
                    # 全码三码字
                    if len(code) == 4:
                        set_code_len3.add(code[:3])
                # 三简字
                elif pat_quick_len3.match(code):
                    set_char_quick_len3.add(dct["char"])
            # (3) 单字快捷兼容(四码字,非常规操作,仅为了方便)
            dict_code_chars = defaultdict(list)
            for dct in self.list_char_code:
                code = dct["code"].rstrip("=")
                # (符合条件的)四码全码字
                if len(code) == 5 and (code[:3] not in set_code_len3):
                    if dct["char"] in set_char_quick_len3:
                        # 设了简的依然排第一
                        dict_code_chars[code[:3]].append({"char":dct["char"], "rank":0})
                    else:
                        # 未设简的取原序
                        dict_code_chars[code[:3]].append({"char":dct["char"], "rank":int(code[-1])})
            # 排序
            n_quick = 0
            for lst in dict_code_chars.values():
                lst.sort(key=lambda d: d["rank"], reverse=False)  # 从低到高排
                n_quick += 1
            # 写入文件
            for code,lst in dict_code_chars.items():
                for i in range(min(len(lst),9)): # 最多取9个
                    fw.write(f"{lst[i]['char']}\t{code}{i+1}+=\t{9-i}\n")
            # (4) 单字快捷兼容(三、四码字,非常规操作,仅为了方便)
            dict_code_chars2 = defaultdict(list)
            for dct in self.list_char_code:
                code = dct["code"].rstrip("=")
                # (符合条件的)四码全码字
                if len(code) in (4,5) and code[:3] in set_code_len3:
                    if dct["char"] in set_char_quick_len3:
                        # 设了简的依然排第一
                        dict_code_chars2[code[:3]].append({"char":dct["char"], "freq":999999})
                    else:
                        # 未设简的取原序
                        dict_code_chars2[code[:3]].append({"char":dct["char"], "freq":dct["freq"]})
            # 排序
            n_quick2 = 0
            for lst in dict_code_chars2.values():
                lst.sort(key=lambda d: d["freq"], reverse=True)  # 从高到低排
                n_quick2 += 1
            # 写入文件
            for code,lst in dict_code_chars2.items():
                for i in range(min(len(lst),9)): # 最多取9个
                    fw.write(f"{lst[i]['char']}\t{code}{i+1}+-\t{9-i}\n")
        print("总组数、5重以上组数、快捷兼容组数、快捷兼容组数2:", n_all, n_above4, n_quick, n_quick2)
        print("已生成文件", file_out)


    def set_quick_code(self, za_flag: str="", yujoy_flag: bool=False):
        list_char_code_new = []
        print("\n---> 开始设置简码...")

        # 1.(可选)设置一二简(一简对应全码字频调为1，二简不变)
        if za_flag:
            pass
        else:
            self.set_quick_code_len1_len2(list_char_code_new)

        # 2.添加兼容码: 含三连击的字(省一击, 不足三码补v), 自定义兼容码
        set_char_compat = set() # 三连击的字
        list_char_code_temp0 = []  # 原编码
        list_char_code_temp = []  # 兼容编码
        pat = re.compile(r"([a-z])\1\1")
        for d in self.list_char_code:
            proc_flag, c = False, "xxxx"
            mth = pat.search(d["code"])
            # (a)三连击
            if mth:
                c = d["code"].replace(mth.group(0), mth.group(0)[:2])
                if len(c) == 2:
                    c += "v"
                proc_flag = True
            # (b)自定义
            elif yujoy_flag and d["char"] == "要":
                c = "wln"
                proc_flag = True
            elif yujoy_flag and d["char"] == "急":
                c = "onv"
                proc_flag = True
            elif yujoy_flag and d["char"] == "绿":
                c = "onv"
                proc_flag = True
            if proc_flag:
                list_char_code_temp0.append({
                    "char": d["char"],
                    "code": d["code"],
                    "freq": d["freq"]
                })
                list_char_code_temp.append({
                    "char": d["char"],
                    "code": c,
                    "freq": d["freq"]
                })
                d["code"] = c
                set_char_compat.add(d["char"])
        self.list_char_code += list_char_code_temp0
        print("添加了兼容码的字数:", len(set_char_compat))

        # 3.设置"三简"(在3-4码字的范围只设一个，相应的全码字频调成该码组里的第2)
        self.list_char_code.sort(key=lambda d: d["freq"], reverse=True)  # 按词频排序(从高到低)
        dict_code_chars = compute_char_chongma(self.list_char_code, True)
        set_qc3 = set()
        dict_code_char_temp = {}
        n_qc3_char = 0
        set_temp = set()
        for d in self.list_char_code:
            # 由于列表已排好序, 那么首次满足该条件的便是最高频字
            if len(d["code"]) >= 3 and (d["code"][:3] not in set_qc3) and (d["char"] not in self.set_qc_char):
                # a.设简
                list_char_code_new.append({
                    "char": d["char"],
                    "code": d["code"][:3].ljust(5, "="),
                    "freq": d["freq"]
                })
                # b.调整原全码词频，如果有重就调到原第2名的后面(比它小0.5), 但如果原第2名过于生僻就没必要
                freq = d["freq"]
                try:
                    code_2rd_char = dict_code_chars[d["code"]][1]
                    freq_2rd_char = next(d["freq"] for d in self.list_char_code if d["char"] == code_2rd_char)
                    if freq_2rd_char <= 2 and freq > 2:
                        pass
                    else:
                        freq = freq_2rd_char - 0.5
                except IndexError:
                    pass
                list_char_code_new.append({
                    "char": d["char"],
                    "code": (d["code"]+"1").ljust(5, "="),
                    "freq": freq
                })
                n_qc3_char += 1
                set_qc3.add(d["code"][:3])  # 收集简码
                dict_code_char_temp[d["code"]] = d["char"]  # 收集原全码映射
                set_temp.add(d["char"])  # 收集设简的字
        self.set_qc_char |= set_temp
        assert n_qc3_char == len(set_qc3)  # 检查一个前三码是否只设置了一个"简"
        print("设置了“三简”的字数:", n_qc3_char)  # 10,233 (rc5)

        # 4.补充剩余部分
        # (a)未设简的三连击全码
        for d in itertools.chain(list_char_code_temp0, list_char_code_temp):
            if not (d["code"] in dict_code_char_temp and dict_code_char_temp[d["code"]] == d["char"]):
                code = (d["code"]+"1").ljust(5, "=")
                list_char_code_new.append({
                    "char": d["char"],
                    "code": code,
                    "freq": d["freq"]
                })
        # (b)其他
        for d in self.list_char_code:
            if not (d["char"] in self.set_qc_char or d["char"] in set_char_compat):
                code = (d["code"]+"1").ljust(5, "=")
                list_char_code_new.append({
                    "char": d["char"],
                    "code": code,
                    "freq": d["freq"]
                })
        # assert len(list_char_code_new) == len(self.list_char_code) + len(self.set_qc_char) # 不再会相等
        self.list_char_code = list_char_code_new

    def set_quick_code_len1_len2(self, list_char_code_new: list) -> None:
        print("开始设置单字的一二简...")
        # 1.读取自定义的单字一二简码
        dict_char_code = {}
        with open(self.file_quick1, 'r', encoding='utf-8') as fr:
            for line in fr:
                char, code = line.strip().split("\t")
                if len(char) == 1:  # 确保是单字
                    dict_char_code[char] = code
        # 2.设置一二简(一简对应全码字频调为1，二简不变)
        for d in self.list_char_code:
            if d["char"] in dict_char_code:
                # 一简对应全码字频调为1
                if len(dict_char_code[d["char"]]) == 1:
                    self.set_qc_char.add(d["char"])
                    # 简码
                    list_char_code_new.append({
                        "char": d["char"],
                        "code": dict_char_code[d["char"]]+"1===",
                        "freq": d["freq"]
                    })
                    # 全码
                    list_char_code_new.append({
                        "char": d["char"],
                        "code": (d["code"]+"1").ljust(5, "="),
                        "freq": 1
                    })
                # 二简的全码字频不变，全码后面再加
                elif len(dict_char_code[d["char"]]) == 2:
                    # 简码
                    list_char_code_new.append({
                        "char": d["char"],
                        "code": dict_char_code[d["char"]]+"1==",
                        "freq": d["freq"]
                    })
        # 若不设一简，原三码阶段的重码情况
        # for d in list_char_code_new:
        #     code_full = d["code"].strip("1=")
        #     chars_c3 = []
        #     if len(code_full) >= 3:
        #         for d2 in self.list_char_code:
        #             if d2["code"][:3] == code_full[:3]:
        #                 chars_c3.append(d2["char"])
        #                 if len(chars_c3) == 3:
        #                     break
        #         print(d["char"], code_full[:3], chars_c3)
        # 若不设一简，原全码阶段的重码情况
        # for char in self.set_qc_char:
        #     code_full = next(d["code"] for d in self.list_char_code d["char"] == char)
        #     print("该一简原所在的全码组:", dict_code_chars[d["code"]])
        print("设置了一简的字数:", len(self.set_qc_char))
        print("设置了二简的字数:", len(dict_char_code)-len(self.set_qc_char))

    def set_choice_mark(self):
        # 1.获取重码数据
        dict_code_chars = compute_char_chongma(self.list_char_code, True)
        # 检查数据是否正常(正常情况下，简码不应该有多重)
        # for code, chars in dict_code_chars.items():
        #     if len(chars) >= 2 and "1" not in code:
        #         print("wrong:", code, chars)
        #         break
        print("\n---> 开始标记重码...")
        # 2.开始标记多选字(2,3,...)
        n_max_quick = 1
        # d_max_quick = {}
        # n_max_chars = ""
        dict_2to9_mark = {}  # 用于收集标记结果
        lst_len = len(self.list_char_code)
        for code, chars in dict_code_chars.items():
            if len(chars) > 1:
                # 由于 self.list_char_code 已排好序, 因而第一个匹配到的便是最高频的那个(不标记)
                n = 0
                for i in range(lst_len):
                    d = self.list_char_code[i]
                    if d["code"] == code:  # code中一定包含标记"1"
                        n += 1
                        if n >= 2:
                            # 收集重码标记(每次的i肯定不一样)
                            dict_2to9_mark[i] = {
                                "char": d["char"],
                                "code": d["code"].replace("1", str(min(n,9)), 1),  # 不超过9
                                "freq": d["freq"]
                            }
                            if d["char"] in self.set_qc_char and n > n_max_quick:
                                n_max_quick = n
                                # d_max_quick = d  # 取样一个
                                # if n_max_quick == 4:  # 收集最远的那些
                                #     n_max_chars += d["char"]
        # 应用标记结果到原码表
        for i in range(lst_len):
            if i in dict_2to9_mark:
                self.list_char_code[i] = dict_2to9_mark[i]
        print("有设简的字的最大候选位:", n_max_quick)

    def generate_dict_yaml_dz(self, list_char_code_ext: list) -> None:
        occupied_codes_len3 = set()  # 三码占用
        # 1.part 1 (基础字集)
        dict_name = "chars"
        fp1 = os.path.join(self.dir_out, dict_name+".dict.yaml")
        with open(fp1, 'w', encoding='utf-8') as fw:
            yaml_header = get_dict_yaml_header(dict_name, self.version, f"三码{self.sname}·基础字集", f"包含 {len(self.set_base)} 汉字(包含『〇』，但不包含21个兼容字)")
            fw.write(yaml_header)
            fw.write("# --- 基础字集码表 ---\n")
            for d in self.list_char_code:
                if d['char'] != "∎":
                    fw.write(f"{d['char']}\t{d['code']}\t{d['freq']}\n")
                    if d["code"].endswith("=="): # 三码简码, 混入了二码也没关系
                        occupied_codes_len3.add(d["code"].rstrip("1="))
        print("已生成基础字集的单字码表文件", fp1)
        
        # 2.part 2 (扩展字集)
        dict_name = "chars_ext"
        fp2 = os.path.join(self.dir_out, dict_name+".dict.yaml")
        with open(fp2, 'w', encoding='utf-8') as fw:
            yaml_header = get_dict_yaml_header(dict_name, self.version, f"三码{self.sname}·扩展字集", f"包含 {len(list_char_code_ext)} 汉字(包含全部472个兼容字)")
            fw.write(yaml_header)
            fw.write("# --- 扩展字集码表 ---\n")
            for d in list_char_code_ext:
                fw.write(f"[超集字]{d['char']}[超]\t{d['code']}\t{d['freq']}\n")
        print("已生成扩展字集的单字码表文件", fp2)
        
        # 3.part 3 (填充剩余的空码位，以单字码表的形式生成)
        # 加载预设(二三简词), 检查二简词(三简不检查)
        with open(self.file_quick2, 'r', encoding='utf-8') as fr:
            for line in fr:
                code = line.strip().split("\t")[-1]
                if len(code) == 3 and code[0] == "z":
                    occupied_codes_len3.add(code)
        dict_name = "chars_none"
        fp = os.path.join(self.dir_out, dict_name+".dict.yaml")
        n3 = 0
        with open(fp, 'w', encoding='utf-8') as fw:
            yaml_header = get_dict_yaml_header(dict_name, self.version, f"三码{self.sname}·填充符号", f"填充所有空余码位，用于标识错误的输入")
            fw.write(yaml_header)
            fw.write("# --- 填充符号码表 ---\n")
            for a in "abcdefghijklmnopqrstuvwxyz":  # 还漏了z,不过影响不大
                for b in "abcdefghijklmnopqrstuvwxyz":
                    for c in "abcdefghijklmnopqrstuvwxyz":
                        code_len3 = a+b+c
                        if code_len3 not in occupied_codes_len3:
                            fw.write(f"⊗\t{code_len3}==\t1\n")
                            fw.write(f"⊗\t{code_len3}1=\t1\n")
                            n3 += 1
        print(f"共填充三码空码位数：", n3)
        print("已生成填充符码表文件", fp)

    def generate_dict_yaml_jianci(self) -> None:
        # --- 0.计算已使用的码位, 剩余可用的码位 ---
        # 已使用的码位
        set_qc1_char = set()
        set_qc2_char = set()
        occupied_codes = set()  # 一码或两码
        dict_char_c1 = {}  # 每个单字的头一码
        for d in self.list_char_code:
            if d["code"].endswith("1==="):   # 一简码位
                set_qc1_char.add(d["char"])
                occupied_codes.add(d["code"][0])
            elif d["code"].endswith("1=="):  # 二简码位
                set_qc2_char.add(d["char"])
                occupied_codes.add(d["code"][:2])
            dict_char_c1[d["char"]] = d["code"][0]
        # 剩余可用的码位
        vacant_codes_len2 = set()
        for a in "abcdefghijklmnopqrstuvwxyz":
            for b in "abcdefghijklmnopqrstuvwxyz":
                code_len2 = a+b
                if code_len2 not in occupied_codes:  # 没有被二简字占用
                    vacant_codes_len2.add(code_len2)

        # --- 1.准备词的简码 ---
        words_len2 = set()
        # 确保是词(根据"现代汉语词典"判断)
        with open("词典/现代汉语词典（第七版）.txt", 'r', encoding='utf-8') as fr:
            for line in fr:
                word = line.strip()
                if len(word) == 2:
                    words_len2.add(word)
        # 给这些词编码
        list_word_code_len2 = []
        for word, freq in self.dict_word_freq.items():
            if len(word) == 2 and (word in words_len2) \
                and set(word).isdisjoint(set_qc1_char) and set(word).isdisjoint(set_qc2_char):
                list_word_code_len2.append({
                    "word": word,
                    "code": "".join(dict_char_c1[char] for char in word),
                    "freq": freq
                })
        list_word_code_len2.sort(key=lambda d: d["freq"], reverse=True)

        # --- 2.开始设简(一二简词) ---
        dict_word_code = {}
        # 加载预设(一简词)
        # with open(self.file_quick1, 'r', encoding='utf-8') as fr:
        #     for line in fr:
        #         word, code = line.strip().split("\t")
        #         if len(code) == 1 and len(word) >= 2:
        #             dict_word_code[word] = code
        # 加载预设(二三简词), 检查二简词(三简不检查)
        with open(self.file_quick2, 'r', encoding='utf-8') as fr:
            for line in fr:
                word, code = line.strip().split("\t")
                if len(code) in (2, 3):
                    dict_word_code[word] = code
                    if len(code) == 2:
                        vacant_codes_len2.discard(code)
                    if code in occupied_codes:
                        print("[提示]该编码已被占用，设置该简词将需要选重:", word, code)
        # 补充剩余空缺码位
        n_q2 = 0
        vacant_codes_len2_done = set()
        for code in vacant_codes_len2:
            for d in list_word_code_len2:
                if d["code"] == code:
                    dict_word_code[d["word"]] = code
                    n_q2 += 1
                    vacant_codes_len2_done.add(code)
                    break
        print("二简词设置完成，总个数：", n_q2)
        print("仍空缺的二码码位有：", vacant_codes_len2 - vacant_codes_len2_done)
        # 检查高频但未设简的二字词
        # with open('out_len2_not.txt', 'w', encoding='utf-8') as fw:
        #     for i in range(200):
        #         if list_word_code_len2[i]["word"] not in dict_word_code:
        #             fw.write(list_word_code_len2[i]["word"]+"\n")

        # --- 3.输出结果到文件 ---
        dict_name = "words_quick"
        file_out = os.path.join(self.dir_out, dict_name+".dict.yaml")
        with open(file_out, 'w', encoding='utf-8') as fw:
            yaml_header = get_dict_yaml_header("words_quick", self.version, f"三码{self.sname}·简码词", "包含汉字词符号和字母数字")
            fw.write(yaml_header)
            for word, code in dict_word_code.items():
                if len(code) == 2:
                    if word in ("·","需求","努力","感觉","数据","必须","科学","免费","付费", "默认", "兼容", "模型"):  # 由于相应编码有重，调频确保这些词为首选
                        fw.write(f"{word}\t{code}1==\t999999\n")
                    else:
                        fw.write(f"{word}\t{code}1==\t1\n")
                elif len(code) == 3 and code.startswith("z"):
                    fw.write(f"{word}\t{code.ljust(5,'=')}\t1\n")
                else:
                    fw.write(f"{word}\t{code.ljust(5,'=')}\t999999\n")
        print("处理完毕，结果文件:", file_out)

    def generate_other_dicts(self):
        print("---> 开始处理 zwords ...")
        dir_in = "material_common"
        dct = {
            "zwords_idioms.txt": ("zwords_idioms", f"三码{self.sname}·成语名句", "数据源自《现代汉语词典》、《现代汉语句典》、《中华句典大全集》"),
            "zwords_poems.txt": ("zwords_poems", f"三码{self.sname}·古诗词","数据源自《宋词鉴赏大典》、《唐诗三百首便览》、《唐诗宋词全鉴 典藏版》、《唐诗鉴赏辞典》"),
            "zwords_others.txt": ("zwords_others", f"三码{self.sname}·其他杂项","包含人名地名等专有名词, 《100年汉语新词新语大辞典》, 以及从《教育部重編國語辭典》转简而来的词"),
            "zwords_special.txt": ("zwords_special", f"三码{self.sname}·特殊词","包含英文词等"),
            "zwords_special_sup.txt": ("zwords_special_sup", f"三码{self.sname}·特殊词(补充)","包含英文词等(手动编码)")
        }
        # dct_easy_en
        dct_easy_en = {
            "base.txt": ("base", "Easy English - base", "english words (base): from https://github.com/skywind3000/ECDICT and OALD"),
            "special.txt": ("special", "Easy English - special","english words (special)"),
            "len4.txt": ("len4", "Easy English - len4","english words (quickcode, len4)"),
            "len5.txt": ("len5", "Easy English - len5","english words (quickcode, len5)"),
            "len7.txt": ("len7", "Easy English - len7","english words (quickcode, len7)"),
            "len8.txt": ("len8", "Easy English - len8","english words (quickcode, len8)")
        }
        list_easy_en = []
        file_in = os.path.join(dir_in, "easy_en/base.txt")
        counter = defaultdict(int)
        with open(file_in, 'r', encoding='utf-8') as fr:
            freq_base = 200_000
            code_len4 = ""
            code_len5 = ""
            code_len7 = ""
            code_len8 = ""
            punc_pat = re.compile(r"[\-+:;/0123456789'\. ]")
            for line in fr:
                word = line.strip()
                code = punc_pat.sub("", word.lower())
                list_easy_en.append({"fname": "base.txt", "word": word, "code": code, "freq": freq_base})
                if len(code) > 4 and counter[code[:4]] < 5:
                    code_len4 = code[:4]
                    list_easy_en.append({"fname": "len4.txt", "word": word, "code": code_len4, "freq": 20-counter[code_len4]})
                    counter[code_len4] += 1
                if len(code) > 5 and counter[code[:5]] < 5:
                    code_len5 = code[:5]
                    list_easy_en.append({"fname": "len5.txt", "word": word, "code": code_len5, "freq": 10-counter[code_len5]})
                    counter[code_len5] += 1
                if len(code) > 7 and counter[code[:7]] < 5:
                    code_len7 = code[:7]
                    list_easy_en.append({"fname": "len7.txt", "word": word, "code": code_len7, "freq": 10-counter[code_len7]})
                    counter[code_len7] += 1
                if len(code) > 8 and counter[code[:8]] < 5:
                    code_len8 = code[:8]
                    list_easy_en.append({"fname": "len8.txt", "word": word, "code": code_len8, "freq": 10-counter[code_len8]})
                    counter[code_len8] += 1
                freq_base -= 1
        # 1.加载所有zwords
        list_word_code_all = []
        freq_special = 300_000
        for fname in os.listdir(dir_in):
            file_in = os.path.join(dir_in, fname)
            if fname in dct and "zwords_special." in fname:
                # 自动生成编码
                for d in get_encoded_words_en(file_in):
                    list_word_code_all.append({
                        "fname": fname,
                        "word": f" {d["word"]} ",
                        "code": d["code"],
                        "freq": freq_special
                    })
                    list_easy_en.append({"fname": "special.txt", "word": d["word"], "code": d["code"], "freq": freq_special})
                    if len(d["word"]) < 4:
                        list_easy_en.append({"fname": "special.txt", "word": d["word"], "code": d["code"][:len(d["word"])], "freq": freq_special})
                    freq_special -= 1
            elif fname in dct and "zwords_special_sup." in fname:
                # 直接从文件读取编码
                with open(file_in, 'r', encoding='utf-8') as fr:
                    for line in fr:
                        word, code = line.strip().split("\t", 1)
                        list_word_code_all.append({
                            "fname": fname,
                            "word": f" {word} ",
                            "code": code,
                            "freq": freq_special
                        })
                        list_easy_en.append({"fname": "special.txt", "word": word, "code": code, "freq": freq_special})
                        if len(word) < 4:
                            list_easy_en.append({"fname": "special.txt", "word": word, "code": code[:len(word)], "freq": freq_special})
                        freq_special -= 1
            elif fname in dct:
                # 自动生成编码
                for d in get_encoded_words(file_in, self.dict_char_codes):
                    list_word_code_all.append({
                        "fname": fname,
                        "word": d["word"],
                        "code": d["code"],
                        "freq": self.dict_word_freq.get(d['word'],2)
                    })
        # 2.计算排名(选重)
        list_word_code_all.sort(key=lambda d: d["freq"], reverse=True)  # 重码率大概50%, 4重以上3000多组
        freq_var = 300_000
        for d in list_word_code_all:  # 重新赋值词频(避免同频，这样能确保与Rime程序的排序一致)
            d["freq"] = freq_var
            freq_var -= 1
        dict_word_mark = {}
        dict_code_words = compute_char_chongma(list_word_code_all, True)
        for code, words in dict_code_words.items():
            rank = 0
            for word in words:
                if rank == 0:
                    dict_word_mark[code+word] = "="
                else:
                    dict_word_mark[code+word] = str(min(rank, 9))
                rank += 1
        # 3.输出到文件(zwords)
        for fname in dct:
            yaml_header = get_dict_yaml_header(dct[fname][0], self.version, dct[fname][1], dct[fname][2])
            file_out = os.path.join(self.dir_out, dct[fname][0]+".dict.yaml")
            with open(file_out, 'w', encoding='utf-8') as fw:
                fw.write(yaml_header)
                for d in list_word_code_all:
                    if d["fname"] == fname:
                        fw.write(f"{d['word']}\tz{d['code']}{dict_word_mark.get(d['code']+d['word'],'=')}=\t{d['freq']}\n")  # 添加z前缀
            print("已生成文件", file_out)
        # 4.输出到文件(easy_en)
        for fname in dct_easy_en:
            yaml_header = get_dict_yaml_header(dct_easy_en[fname][0], self.version, dct_easy_en[fname][1], dct_easy_en[fname][2])
            dir_out = os.path.join(os.path.split(self.dir_out)[0], "dicts_easy_en")
            file_out = os.path.join(dir_out, dct_easy_en[fname][0]+".dict.yaml")
            with open(file_out, 'w', encoding='utf-8') as fw:
                fw.write(yaml_header)
                for d in list_easy_en:
                    if d["fname"] == fname:
                        fw.write(f"{d['word']}\t{d['code']}\t{d['freq']}\n")
            print("已生成文件", file_out)

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    myschema = SchemaYujoyFluid(
        "material_yujoy",
        "yujoy.full.dict_v3.6.0.yaml",
        "schema_yujoy_fluid/dicts_yujoy_fluid",
        "卿云",
        "2.4"
    )
    myschema.build("", True)
    # myschema = SchemaYujoyFluid(
    #     "material_yujoy",
    #     "yujoy.full.dict_v3.6.0.yaml",
    #     "schema_yujoy_fluid/dicts_yujoy_fluid_a",
    #     "卿云",
    #     "2.4"
    # )
    # myschema.build("A", True)  # a版
    # myschema.generate_other_dicts()
    print("\nRuntime:", time.perf_counter() - start)

"""
 --- 0.字集 ---
 * 全部汉字分成两部分，3万字基础集，3万字以外的超集(7万左右)
 --- 1.字频 ---
 * 字频: 有频的最小3, 无频的设默认值2(常规最小), 有设简的全码字频调到第二, 3万字以外的(超集)一律设值0
 * 设简: 
 *    三简: 4码字设三简的条件是最高频(在前3码开头的所有字中最高), (相应全码编码字频调到第二)
 *    二简: 自定义二简字(后一码为a或k, 个别可能为do), 剩余空码位可设置二简词或标点符号等
 *    一简: 一简的相应全码编码字频调为1
 * 兼容码: 含三连击的字添加兼容码(省一击, 结果不足三码补v)
 --- 2.标记 ---
 * (经过以下规则后, 不足5码的补0，即所有字都统一5码，这方便给4码字标记选重)
 * 1码编码:
 *    全码1码: 无重，只有标记1(格式如"a1===", 补“_”出)，不存在"a===="这种编码
 * 2码编码:
 *    全码2码: 按词频依次标记1-9(格式如"aa1==", 补“_”出；如"aa2==", 补“__”出)，不存在"aa==="这种编码
 * 3码编码:
 *    简码3码: 不标(格式如"aaa==", 因为已经最高频, 且与全码区分)
 *    全码3码: 按词频依次标记1-9(格式如"aaa1=", 补“/”出；如"aaa2=", 补“/_”出)
 * 4码编码:
 *    全码4码：按词频依次标记1-9(格式如"aaaa1", 补“/”出；如"aaaa2", 补“/_”出)，不存在"aaaa="这种编码
 --- 3.组词 ---
 * 组词: 所有单字的各种编码都参与组词，一个单字最多可能有5种编码(一或二简，三简，全码标1-9, 兼容码三简，兼容码全码)，常规最多应是4种
"""
