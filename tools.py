from datetime import datetime
import hmac
import hashlib

def get_signature(url, ts, method, nonce):
    """
    生成签名
    :param url: 请求的URL
    :param ts: 时间戳
    :param method: 请求方法 (GET/POST)
    :param nonce: 随机数
    :return: 签名字符串
    """
    apple_kill_flag = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
    apple_version = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
    raw = f"{url}{ts}{nonce}{method}{apple_kill_flag}".lower()
    signature = hmac.new(apple_version.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return signature

def format_time(time_str):
    """
    格式化时间字符串
    :param time_str: 输入的时间字符串
    :return: 格式化后的时间
    """
    try:
        time_str = time_str.replace("：", ":").replace(".", ":")
        time = datetime.strptime(time_str, "%H:%M")
        return time.strftime("%H:%M")
    except Exception:
        return -1
