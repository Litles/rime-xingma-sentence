#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-10-12 01:16:23
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

from schema_flypy_pro import SchemaFlypyPro

class SchemaZiranmaFluid(SchemaFlypyPro):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, map_shengmu: dict, map_yunmu: dict):
        super().__init__(dir_in, fname_full, dir_out, map_shengmu, map_yunmu)

if __name__ == '__main__':
    import time
    start = time.perf_counter()

    map_shengmu = { "zh": "v", "ch": "i", "sh": "u" }
    map_yunmu = {
        'iu': 'q',
        'ia': 'w', 'ua': 'w',
        'uan': 'r', 'van': 'r',
        'ue': 't', 've': 't',
        'uai': 'y', 'ing': 'y',
        'uo': 'o',
        'un': 'p', 'vn': 'p',
        'iong': 's', 'ong': 's',
        'iang': 'd', 'uang': 'd',
        'en': 'f',
        'eng': 'g',
        'ang': 'h',
        'an': 'j',
        'ao': 'k',
        'ai': 'l',
        'ei': 'z',
        'ie': 'x',
        'iao': 'c',
        'ui': 'v',
        'ou': 'b',
        'in': 'n',
        'ian': 'm'
    }
    myschema = SchemaZiranmaFluid(
        "material_yujoy",
        "yujoy.full.dict_v3.6.0.yaml",
        "schema_ziranma_pro/dicts_ziranma_pro",
        map_shengmu,
        map_yunmu
    )
    myschema.build()

    print("\nRuntime:", time.perf_counter() - start)
