#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024-10-06 00:17:06
# @Author  : Litles (litlesme@gmail.com)
# @Link    : https://github.com/Litles
# @Version : 2.4

from schema_yujoy_fluid import SchemaYujoyFluid

class SchemaTigerFluid(SchemaYujoyFluid):
    def __init__(self, dir_in: str, fname_full: str, dir_out: str, sname: str, version: str):
        super().__init__(dir_in, fname_full, dir_out, sname, version)

if __name__ == '__main__':
    import time
    start = time.perf_counter()
    # myschema = SchemaTigerFluid(
    #     "material_tiger",
    #     "tiger.dict.yaml",
    #     "schema_tiger_fluid/dicts_tiger_fluid",
    #     "虎码",
    #     "2.4"
    # )
    # myschema.build()
    myschema = SchemaTigerFluid(
        "material_tiger",
        "tiger.dict.yaml",
        "schema_tiger_fluid/dicts_tiger_fluid_a",
        "虎码",
        "2.4"
    )
    myschema.build("A")  # a版
    print("\nRuntime:", time.perf_counter() - start)
