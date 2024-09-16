class Headers:
    def __init__(self) -> None:
        self.headers = {}

    def set_header(self, key, value):
        self.headers[key] = value

    def del_header(self, key):
        if key in self.headers:
            del self.headers[key]

def create_login_headers():
    login_headers = Headers()
    headers_dict = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': '',
        'Cache-Control': 'no-cache',
        'Content-Length': '51',
        'Content-Type': 'application/json',
        'Origin': 'https://www.mfuns.net',
        'Pragma': 'no-cache',
        'Referer': 'https://www.mfuns.net/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
    }
    for key, value in headers_dict.items():
        login_headers.set_header(key, value)
    return login_headers
