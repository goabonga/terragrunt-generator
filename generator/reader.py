import os

import hcl2


def read_file(path: str) -> dict:
    datas: dict = {}
    with open(path) as file:
        try:
            datas = hcl2.load(file)
        except Exception as error:
            raise error
    return datas


def read_directory(path: str) -> dict:
    datas = {}
    for file in os.listdir(path):
        if file.endswith('.tf'):
            try:
                datas = datas | read_file(f'{path}/{file}')
            except Exception:
                pass
    return datas
