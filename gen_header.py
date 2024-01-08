import binascii
import os
import headers
import utiles
import time

def login_headers():
    login_headers = headers.Headers()
    keys = ['Accept', 
            'Accept-Encoding', 
            'Accept-Language', 
            'Authorization', 
            'Cache-Control',
            'Content-Length', 
            'Content-Type', 
            'Origin', 
            'Pragma',
            'Referer',
            'Sec-Ch-Ua', 
            'Sec-Ch-Ua-Mobile', 
            'Sec-Ch-Ua-Platform', 
            'Sec-Fetch-Dest', 
            'Sec-Fetch-Mode', 
            'Sec-Fetch-Site', 
            'User-Agent']
    values = ['application/json', 
              'gzip, deflate, br', 
              'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6', 
              '', 
              'no-cache', 
              '51', 
              'application/json', 
              'https://www.mfuns.net', 
              'no-cache',
              'https://www.mfuns.net/', 
              '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"', 
              '?0', 
              '"Windows"', 
              'empty', 
              'cors', 
              'same-site', 
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0']
    
    
    for i in range(len(keys)):
        login_headers.set_header(keys[i], values[i])
    return login_headers