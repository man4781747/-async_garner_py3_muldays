# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 13:56:13 2017

@author: FB:橘毛橘毛 Gits:lanfon72
"""

import os
from ftplib import FTP
import asyncio

import aiohttp
from aiofiles import open as aopen


def get_connect(url):
    root, foldr = url.split('//', 1)[-1].split('/', 1)  # root:目標網站  foldr:欲下載檔案位置   
    ftp = FTP(root)                                     # 與目標網站連接
    ftp.login()                                         # 登入(以匿名)
    ftp.cwd(foldr)                                      # 切入至欲下載檔案位置   
    return ftp


async def save_file(path, url, semaphore):
    try:
        async with semaphore, aiohttp.request('GET', url) as r:    # request(method, url) http://aiohttp.readthedocs.io/en/stable/client_reference.html
            data = await r.read()                                  # 使用 aiohttp.request 來"異步"取得目標檔案的資料
        async with aopen(path, 'wb') as f:
            await f.write(data)                                    # 寫入資料
    except Exception as e:
        print("get error on", path, "due to", repr(e))             # 報錯
        return path                                                # 報錯後返回失敗的的檔案名稱
    else:
        print(path, "saved.")                                      # 下載成功
        return None                                                # 下載成功後返回None

async def main(files, url):
    concurrent = asyncio.Semaphore(256)                                                             # ????? 類似平行處理設定CPU數?
    futs = [save_file(f, "%s/%s" % (url, f), concurrent) for f in files]                            # 下載檔案
    done, _ = await asyncio.wait(futs)                                                              # 等待跑完所有檔案???? 
                                                                                                    # asyncio.wait(futures, *, loop=None, timeout=None, return_when=ALL_COMPLETED)
                                                                                                    # 返回值 ( done, pending )
                                                                                                    # https://docs.python.org/3/library/asyncio-task.html#asyncio.Future
    done = [f.result() for f in done]                                                               # 整理出結果清單 (有名稱的為下載失敗 ,None 為下載成功) 
    while any():                                                                                    # 有值就
        print("fail to fetched:", len([i for i in done if i]))                                      # 失敗數
        pending = [save_file(f, "%s/%s" % (url, f), concurrent) for f in filter(None, done)]        # 失敗的檔案再次下載
        done, _ = await asyncio.wait(pending)                                                       # 等待跑完所有檔案???? 
        done = [f.result() for f in done]                                                           # 整理出結果清單 (有名稱的為下載失敗 ,None 為下載成功) 
        
                                                                                                    # 直到下載成功???(如果有爛檔案他會永遠卡住變成DDoS?)


if __name__ == '__main__':
    url = "garner.ucsd.edu/pub/rinex/2003/303"                 # 目標地址
    conn = get_connect(url)
    files = set(conn.nlst()).difference(os.listdir())          # 產生目標資料夾所有檔案的列表且替除已下載檔案的名稱
    conn.quit()                                                # 登出
    if files:
        loop = asyncio.get_event_loop()                        # ???????????????????????????????????????????????????
        url = r'http://anonymous:jason%40ucsd.edu@' + url
        loop.run_until_complete( main(files, url) )