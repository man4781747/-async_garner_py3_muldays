"""
Created on Fri Aug  4 19:02:57 2017

@author: FB:橘毛橘毛 Gits:lanfon72 
"""

import os
#from ftplib import FTP
import asyncio
import subprocess
import aiohttp
from aiofiles import open as aopen

#def get_connect(url):
#    root, foldr = url.split('//', 1)[-1].split('/', 1)  # root:目標網站  foldr:欲下載檔案位置   
#    ftp = FTP(root)                                     # 與目標網站連接
#    ftp.login()                                         # 登入(以匿名)
#    ftp.cwd(foldr)                                      # 切入至欲下載檔案位置   
#    return ftp


async def save_file(path, url, semaphore):
    try:
        if not os.path.isfile(path):
            async with semaphore, aiohttp.request('GET', url) as r:    # request(method, url) http://aiohttp.readthedocs.io/en/stable/client_reference.html
                data = await r.read()                                  # 使用 aiohttp.request 來"異步"取得目標檔案的資料
            async with aopen(path, 'wb') as f:
                await f.write(data)                                    # 寫入資料
    except Exception as e:
        print("get error on", path, "due to", repr(e))             # 報錯
        return path                                                # 報錯後返回失敗的的檔案名稱
    else:
        subprocess.call('uncompress {0}'.format(path).split())
        print(path, "saved.")                                      # 下載成功
        return None                                                # 下載成功後返回None

async def main(url, fnamelist, doy_list, year_list):
    concurrent = asyncio.Semaphore(256)                                                             # 最大線程數
    futs = []
    fmt = "%s{y}/{d:03d}/{f}{d:03d}0.{y}d.Z"
    items = [fmt.format(y=y, d=d, f=f) for y in year_list for d in doy_list for f in fname_list]
    futs = [save_file(i % "./rinex/20", i % url, concurrent) for i in items]                         # 下載檔案 (檔案名稱(包含儲存路徑), 檔案路徑, concurrent)
    done, _ = await asyncio.wait(futs)                                                              # 等待跑完所有檔案???? 
                                                                                                    # asyncio.wait(futures, *, loop=None, timeout=None, return_when=ALL_COMPLETED)
                                                                                                    # 返回值 ( done, pending )
                                                                                                    # https://docs.python.org/3/library/asyncio-task.html#asyncio.Future
    done = [f.result() for f in done]                                                               # 整理出結果清單 (有名稱的為下載失敗 ,None 為下載成功) 
    while any(done):                                                                                # 有值就
        print("fail to fetched:", len([i for i in done if i]))                                      # 失敗數
        pending = [save_file(f, "%s/%s" % (url, f), concurrent) for f in filter(None, done)]        # 失敗的檔案再次下載
        done, _ = await asyncio.wait(pending)                                                       # 等待跑完所有檔案???? 
        done = [f.result() for f in done]                                                           # 整理出結果清單 (有名稱的為下載失敗 ,None 為下載成功) 
        
                                                                                                    # 直到下載成功???(如果有爛檔案他會永遠卡住變成DDoS?)
if __name__ == '__main__':
    url = "garner.ucsd.edu/pub/rinex/20"                 # 目標地址
    year_list = ['03']
    doy_list = range(1,3)
    
    
#    fname_list = ['zimm']
    
    with open('station_list.txt') as fname:
        fname_list = []
        rl = fname.readlines()
        for s in rl:
            fname_list.append(s[0:4])

    fmt = "./rinex/20{0}/{1:03d}"
    dirs = [fmt.format(y, d) for y in year_list for d in doy_list]
    [os.makedirs(d) for d in dirs if not os.path.exists(d)]

#    conn = get_connect(url)
#    files = set(conn.nlst()).difference(os.listdir())          # 產生目標資料夾所有檔案的列表且替除已下載檔案的名稱
#    conn.quit()                                                # 登出
    if fname_list:
        loop = asyncio.get_event_loop()
        url = r'http://anonymous:jason%40ucsd.edu@' + url
        loop.run_until_complete( main(url, fname_list, doy_list, year_list) )
