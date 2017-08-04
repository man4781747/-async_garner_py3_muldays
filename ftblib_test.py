# -*- coding: utf-8 -*-
"""
Created on Thu Aug 03 22:51:12 2017

@author: FB:橘毛橘毛
"""

from ftplib import FTP


def get_connect(url):
    root, foldr = url.split('//', 1)[-1].split('/', 1)  # root:目標網站  foldr:欲下載檔案位置   
    ftp = FTP(root)                                     # 與目標網站連接
    ftp.login()                                         # 登入(以匿名)
    ftp.cwd(foldr)                                      # 切入至欲下載檔案位置   
    return ftp


def download_file(ftp, filename):
    try:
        with open(filename, 'wb') as f:
            ftp.retrbinary("RETR %s" % filename, f.write)     # 用 `cmd` 取得檔案的 binary data, `callback` 寫入 file as f.
    except Exception as e:
        print(e)                                              # 報錯
        ftp.quit()                                            # 登出
        return None, None
    else:
        return ftp, filename                                  # 回傳連線狀態 以及 下載的檔案名稱


def main(files, url):
    files = set(files)                                   # 確認檔案不重複            
    ftp = get_connect(url)                               # 切入至欲下載檔案位置                   
    fname = files.pop()                                  # 從file清單中挑出一項並不放回
    while files:
        ftp, fname = download_file(ftp, fname)           # 下載檔案 並回傳連線狀態 以及 下載的檔案名稱
        ftp = ftp if ftp else get_connect(url)           # 若 download_file 時有斷連結則重新連結
        fname = files.pop() if fname else fname          # 如果檔案名稱已用過 再次從file清單中挑出一項並不放回 

if __name__ == '__main__':
    url = "garner.ucsd.edu/pub/rinex/2003/302"           # 目標地址
    conn = get_connect(url)
    files = conn.nlst()                                  # 產生目標資料夾所有檔案的列表
    conn.quit()                                          # 登出
    main(files, url)                                     # 載檔案瞜