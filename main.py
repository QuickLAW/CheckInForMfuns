import logging
import os
import time
import requests
import headers
import gen_header
import schedule
import tools
# 应对数据包br压缩而导入的库
# 不导入直接打包requests获取的数据可能乱码
# 也可以在请求头中去除br来规避
import brotli

class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

class Session_Manager():
    def __init__(self) -> None:
        self.session = requests.session()
        self.headers = headers.Headers
        self.headers_with_token = headers.Headers
        self.login_api = 'https://api.mfuns.net/v1/auth/login'
        self.account_data_api = 'https://api.mfuns.net/v1/user/info'
        self.sign_list_api = 'https://api.mfuns.net/v1/sign/sign_list'
        self.daily_award_api = 'https://api.mfuns.net/v1/sign/daily_awards'
        self.sign_api = 'https://api.mfuns.net/v1/sign/sign'
        self.token = ''
        self.token_file = 'token'
        self.username = ''
        self.password = ''
        self.account_is_right = False

        self.logger = logging.getLogger()
        self.__init_logger__()

    def __init_logger__(self):
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于输出到控制台
        ch_info = self.create_handler(logging.INFO, LevelFilter(logging.INFO), '[Mfuns] %(asctime)s %(levelname)s : %(message)s')
        ch_error = self.create_handler(logging.ERROR, LevelFilter(logging.ERROR), '\033[0;31m[Mfuns] %(asctime)s %(levelname)s : %(message)s\033[0m')
        ch_warn = self.create_handler(logging.WARNING, LevelFilter(logging.WARNING), '\033[0;33m[Mfuns] %(asctime)s %(levelname)s\033[0m : %(message)s')

        # 给logger添加handler
        self.logger.addHandler(ch_info)
        self.logger.addHandler(ch_error)
        self.logger.addHandler(ch_warn)

    def create_handler(self, level, filter, formatter):
        # 创建一个日志处理器，设置其日志级别，过滤器和格式化器
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.addFilter(filter)
        handler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
        return handler

    def input_username_and_password(self):
        # 如果账户信息不正确，则提示用户输入用户名和密码
        if not self.account_is_right:
            self.username = input("请输入账号：")
            self.password = input("请输入密码：")

            if self.password == '' or self.username == '':
                self.logger.warning("输入不能为空！")
                self.input_username_and_password()
            else:
                self.login()

    def login(self):
        # 使用用户提供的用户名和密码进行登录
        data = {
            "account": self.username,
            "password": self.password
        }
        self.headers = gen_header.login_headers()
        r = self.session.post(url=self.login_api, json=data, headers=self.headers.headers)
        if r.status_code == 200:
            if r.json()['code'] == 1:
                self.logger.info("登录成功！")
                self.token = r.json()['data']['access_token']
                self.save_token()
                self.token_in_headers()
            else:
                self.logger.error("登录失败！")
                self.logger.error(r.json()['msg'])
                self.logger.warning("请重新登录")
                self.input_username_and_password()

    def token_in_headers(self):
        # 将token添加到请求头中
        self.headers_with_token = gen_header.login_headers()
        self.headers_with_token.set_header('Authorization', self.token)
        self.headers_with_token.del_header('Content-Length')
        self.headers_with_token.del_header('Content-Type')

    def save_token(self):
        # 将token保存到文件中
        if not os.path.exists(self.token_file):
            with open(self.token_file, 'w') as f:
                f.write('')
        with open(self.token_file, 'w') as f:
            if self.token == '':
                self.logger.error("token竟然为空！请联系开发者解决")
            f.write(self.token)

    def load_token(self):
        # 从文件中加载token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                self.token = f.read()
                if self.token == '':
                    self.logger.warning("token不存在，请登录")
                    self.input_username_and_password()
                else:
                    self.token_in_headers()
        else:
            self.logger.warning("token不存在，请登录")
            self.input_username_and_password()

    def get_data(self, url):
        # 从给定的URL获取数据
        r = self.session.get(url=url, headers=self.headers_with_token.headers)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            self.logger.error("token错误！！尝试重新登录")
            self.input_username_and_password()
            self.display_account_data()
        else:
            self.logger.error("获取数据出错！")
            self.logger.error(f"错误代码：{r.status_code}")
            return -1

    def get_account_data(self):
        # 获取账户数据
        return self.get_data(self.account_data_api)

    def get_sign_list(self):
        # 获取签到列表
        return self.get_data(self.sign_list_api)

    def get_daily_award(self):
        # 获取每日奖励
        return self.get_data(self.daily_award_api)

    def sign(self):
        # 进行签到
        self.logger.info('正在开始签到...')
        r = self.session.get(url=self.sign_api, headers=self.headers_with_token.headers)
        if r.status_code == 200:
            self.logger.info(r.json()['msg'])
            if r.json()['code'] == 1:
                self.logger.info("今日签到成功！！")
            elif r.json()['code'] == 0:
                self.logger.warning(r.json()['msg'])
            self.after_sign_display_data()

    def auto_sign(self):
        # 自动签到
        while True:
            input_time = input("请输入每天定时签到的时间(格式 HH:MM): ")
            input_time = tools.format_time(input_time)
            if input_time != -1:
                self.logger.info(f"每日签到时间设定为：{input_time}")
                schedule.every().day.at(input_time).do(self.sign)
                while True:
                    schedule.run_pending()
                    time.sleep(30)
            else:
                self.logger.warning("输入格式错误")

    def display_account_data(self, account_data):
        # 显示账户数据
        if account_data == -1:
            return
        level_list = ['D级', 'D+级', 'C级', 'C+级', 'B级', 'B+级', 'A级', 'A+级', 'S级', 'S+级', '花好月圆', '虎年大吉', '纯爱战士', '爱国者', 'NTR达人', 'NTR冠军', '靓', '金皮卡', '月曼中秋', 'VIP', '劳动节']
        self.logger.info(f"昵称：{account_data['data']['user']['name']}")
        self.logger.info(f"ID：{account_data['data']['user']['id']}")
        self.logger.info(f"喵币：{account_data['data']['user']['neko_coin']}")
        self.logger.info(f"当前等级：{level_list[account_data['data']['user']['level_badge'] - 1]}")
        self.logger.info(f"当前经验值：{account_data['data']['user']['exp']}")

    def after_sign_display_data(self):
        # 签到后显示数据
        account_data = self.get_account_data()
        self.display_daily_award()
        self.display_account_data(account_data)

    def display_daily_award(self):
        # 显示每日奖励
        daily_award = self.get_daily_award()
        if daily_award != -1:
            self.logger.info(f"今日获得：{daily_award['data'][0]['desc']}，{daily_award['data'][1]['desc']}")

    def display_sign_list(self):
        # 显示签到列表
        sign_list = self.get_sign_list()
        if sign_list != -1:
            self.logger.info(f"本月签到{sign_list['data']['month_times']}天")
            self.logger.info(f"总共签到：{sign_list['data']['all_times']}天")

    def run(self):
        # 运行程序
        self.load_token()
        self.display_account_data(self.get_account_data())
        self.sign()
        self.auto_sign()

        
session = Session_Manager()

session.run()
