#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-09-07 00:42:52
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

import os
import re
from schema_yujoy_fluid import SchemaYujoyFluid

class SchemaYustarFluid(SchemaYujoyFluid):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        super().__init__(dir_in, fname_full, dir_out, sname, version)
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
    myschema = SchemaYustarFluid(
        "material_yustar",
        "yustar.full.dict_v3.6.0.yaml",
        "schema_yustar_fluid/dicts_yustar_fluid",
        "星陈",
        "2.0"
    )
    myschema.build()
    # myschema = SchemaYustarFluid(
    #     "material_yustar",
    #     "yustar.full.dict_v3.6.0.yaml",
    #     "schema_yustar_fluid/dicts_yustar_fluid_z",
    #     "星陈",
    #     "2.0"
    # )
    # myschema.build(True)  # z版
    # myschema.generate_other_dicts()
    print("\nRuntime:", time.perf_counter() - start)
