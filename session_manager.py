import json
import logging
import requests
import schedule
import time
import brotli
from headers import create_login_headers
from tools import format_time
from config import load_config, save_config, update_token

class LevelFilter(logging.Filter):
    """A filter to allow logging only specific levels."""
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.headers = create_login_headers()
        self.config = load_config()
        self.token = self.config.get('token', '')
        self.logger = self._init_logger()
        self._schedule_token_refresh()
        self.auto_sign_flag = False

    def _init_logger(self):
        """Initialize the logger with multiple handlers for different log levels."""
        logger = logging.getLogger("Mfuns")
        logger.setLevel(logging.DEBUG)
        # Add INFO, ERROR, and WARNING handlers
        for level, color_code in [(logging.INFO, ''), 
                                  (logging.ERROR, '\033[0;31m'), 
                                  (logging.WARNING, '\033[0;33m')]:
            logger.addHandler(self._create_handler(level, f'{color_code}[Mfuns] %(asctime)s %(levelname)s : %(message)s\033[0m'))
        return logger

    def _create_handler(self, level, formatter):
        """Helper method to create log handlers with filters."""
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
        handler.addFilter(LevelFilter(level))
        return handler

    def _schedule_token_refresh(self):
        """Set up a token refresh schedule based on config or default interval."""
        interval = self.config.get('token_refresh_interval', 21600)  # Default is 6 hours
        schedule.every(interval).seconds.do(self.refresh_token)

    def refresh_token(self):
        """Automatically refresh token by re-logging in."""
        self.logger.info("自动刷新token...")
        self.login(self.config['username'], self.config['password'])

    def login(self, username, password):
        """Handle user login and update token."""
        data = {"account": username, "password": password}
        try:
            r = self.session.post(url='https://api.mfuns.net/v1/auth/login', json=data, headers=self.headers.headers)
            response_json = self._handle_response(r, "登录失败")
            if response_json and response_json.get('code') == 1:
                self._on_login_success(response_json['data']['access_token'])
                self.auto_sign_flag = True
            if response_json and response_json.get('code') == 10002:
                self.logger.error("账号或用户名错误！")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")

    def _on_login_success(self, new_token):
        """Handle actions to perform after successful login."""
        self.logger.info("登录成功！")
        update_token(new_token)
        self.token = new_token
        self._update_headers()

    def _handle_response(self, response: requests.Response, error_msg):
        """Helper method to parse JSON responses."""
        try:
            if response.headers.get('Content-Encoding') == 'br':
                # 使用brotli解压缩内容
                decompressed_data = brotli.decompress(response.content)
                # 将解压缩后的数据转换为字符串（假设返回内容是文本）
                response_text = decompressed_data.decode('utf-8')
                json_data = json.loads(response_text)
            else:
                json_data = response.json()
            return json_data
        except requests.exceptions.JSONDecodeError:
            self.logger.error(f"无法解析服务器响应，{error_msg}")
        return None

    def _update_headers(self):
        """Update headers with the latest token."""
        self.headers.set_header('Authorization', self.token)
        self.headers.del_header('Content-Length')
        self.headers.del_header('Content-Type')

    def load_token(self):
        """Load token from config or trigger login if token is missing."""
        if not self.token:
            self.logger.warning("Token不存在，正在尝试登录")
            if self.config['username'] == "":
                self.logger.error("请进入config.json文件配置账号密码")
            else:
                self.login(self.config['username'], self.config['password'])
        else:
            self.logger.info("正在使用Token登录")
            self._update_headers()
            self.auto_sign_flag = True

    def auto_sign(self):
        """Prompt user to set up a daily automatic sign-in task."""
        if self.auto_sign_flag:
            # input_time = input("请输入每天定时签到的时间(格式 HH:MM): ")
            formatted_time = format_time(self.config['time'])
            if formatted_time != -1:
                self.logger.info(f"每日签到时间设定为：{formatted_time}")
                schedule.every().day.at(formatted_time).do(self.sign)
                self._start_schedule_loop()
            else:
                self.logger.error("时间格式设置错误！")

    def sign(self):
        """Perform the sign-in action."""
        self.logger.info('正在开始签到...')
        try:
            r = self.session.get(url='https://api.mfuns.net/v1/sign/sign', headers=self.headers.headers)
            response_json = self._handle_response(r, "签到失败")
            if response_json and response_json.get('code') == 1:
                self.logger.info("今日签到成功！！")
            else:
                self.logger.warning(response_json.get('msg', '签到失败'))
        except requests.exceptions.RequestException as e:
            self.logger.error(f"签到请求失败: {e}")

    def _start_schedule_loop(self):
        """Keep the scheduling loop running."""
        while True:
            schedule.run_pending()
            time.sleep(30)

    def run(self):
        """Main run method to load token and start auto sign-in."""
        self.load_token()
        self.auto_sign()

if __name__ == '__main__':
    session = SessionManager()
    session.run()
