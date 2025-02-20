#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-10-06 00:17:06
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 1.0

from schema_yujoy_fluid import SchemaYujoyFluid

class SchemaWubi06Fluid(SchemaYujoyFluid):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        super().__init__(dir_in, fname_full, dir_out, sname, version)

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    # myschema = SchemaWubi06Fluid(
    #     "material_wubi06",
    #     "wubi06_char_full.txt",
    #     "schema_wubi06_fluid/dicts_wubi06_fluid",
    #     "新世纪五笔",
    #     "2.3"
    # )
    # myschema.build()
    myschema = SchemaWubi06Fluid(
        "material_wubi06",
        "wubi06_char_full.txt",
        "schema_wubi06_fluid/dicts_wubi06_fluid_a",
        "新世纪五笔",
        "2.3"
    )
    myschema.build("A")  # A版
    myschema.generate_other_dicts()
    print("\nRuntime:", time.perf_counter() - start)
