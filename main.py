import asyncio
import sys

import httpx

from scrap.scrap import scrap
from analysis.analyse import analyse, compare_analyse


async def main(params: list[str]):
    try:
        if params[1] == "new":
            file_name = await scrap()
            exp = int(params[2]) if len(params) > 2 else None
            analyse(file_name, exp)
        if params[1] == "load":
            file_name = params[2]
            exp = int(params[3]) if len(params) > 3 else None
            analyse(file_name, exp)
        if params[1] == "comp":
            file_name_1 = params[2]
            file_name_2 = params[3]
            exp = int(params[4]) if len(params) > 4 else None
            compare_analyse(file_name_1, file_name_2, exp)
        if params[1] == "help":
            print(
                "new [exp] - new analyse. if exp is nan - analyse all data \n"
                "load [file1] [exp] - analyse exists data. if exp is nan - analyse all data \n"
                "comp [file1] [file2] [exp] - compare two datas. file1 must be older file"
            )
    except IndexError:
        print("Not all parameters added. Print help")
    except FileNotFoundError as e:
        print(e)
    except httpx.ConnectTimeout:
        print("Connection timeout. Try again")


asyncio.run(main(sys.argv))
