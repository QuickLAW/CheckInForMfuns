from datetime import datetime
import hmac
import hashlib
import os
import binascii

def get_signature(url, ts, method, nonce):
    appleKillFlag = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
    appleVerSion = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
    # 将剩余的部分与时间戳、随机数、HTTP方法以及appleKillFlag变量拼接在一起
    raw: str = url + str(ts) + nonce + method + appleKillFlag
    # 将原始字符串转换为小写
    raw = raw.lower()
    signature = hmac.new(appleVerSion.encode(), raw.encode(), hashlib.sha256).hexdigest()
    
    return signature

def format_time(time_str):
    try:
        time_str = time_str.replace("：", ":").replace(".", ":")  # 将全角冒号替换为半角冒号
        time = datetime.strptime(time_str, "%H:%M")
        return time.strftime("%H:%M")
    except Exception:
        return -1
     