import json
import os
import time
from datetime import datetime

import requests
from PyQt5.QtCore import pyqtSignal, QThread

from src.config import cfg
from src.runtimeLog import runtime_log


class AccountManage:
    def __init__(self):
        self.accounts_path = os.path.join(cfg.get(cfg.workDir), 'channels.json')
        try:
            self.orz_accounts = json.load(open(self.accounts_path, 'r', encoding='utf-8'))
        except Exception as e:
            runtime_log.warning(f"加载账号信息失败: {e}")
            self.orz_accounts = []
        self.accounts = self.load_accounts()

        self.login_thread = LoginThread()

    def change_account(self, account):
        pass

    def delete_account(self, account):
        pass

    # 将时间戳转换为字符串
    def load_accounts(self):
        accounts = []
        for account in self.orz_accounts:
            timestamp = account['create_time']
            create_time_str = datetime.fromtimestamp(timestamp).strftime('%m-%d')
            account['create_time'] = create_time_str
            timestamp = account['last_login_time']
            if timestamp == 0:
                last_login_time_str = '未登录'
            else:
                last_login_time_str = datetime.fromtimestamp(timestamp).strftime('%m-%d')
            account['last_login_time'] = last_login_time_str
            accounts.append(account)
        return accounts

    def login_account(self, id: int):
        id_uuid = self.accounts[id]['uuid']
        self.login_thread.uuid = id_uuid
        self.login_thread.start()
        self.login_thread.login_signal.connect(self.login_callback)

    def login_callback(self, status):
        if status:
            runtime_log.info(f"发送登录请求成功: {self.login_thread.uuid}")
        else:
            runtime_log.error(f"发送登录请求失败: {self.login_thread.uuid}")


class LoginThread(QThread):
    login_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.uuid = ''

    def run(self):
        try:
            res = requests.get(f'https://localhost/_idv-login/switch?uuid={self.uuid}', verify=False)
            # 200: 成功
            if res.status_code == 200:
                self.login_signal.emit(True)
            else:
                self.login_signal.emit(False)
        except Exception as e:
            runtime_log.error(f"发送登录请求失败: {self.uuid}, {e}")
            self.login_signal.emit(False)
        return


class CheckLoginFinishThread(QThread):
    check_login_finish_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        # Using shell=True to allow runas command
        login_proxy_log_path = os.path.join(cfg.get(cfg.workDir), 'idv-login-log.txt')
        if not os.path.exists(login_proxy_log_path):
            self.check_login_finish_signal.emit(-1)
            runtime_log.warning(f"登录器未启动")
            return
        # POST /mpay/api/users/login/qrcode/exchange_token
        # 输出
        timer = 0
        while True:
            time.sleep(0.5)
            with open(login_proxy_log_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
                for line in lines:
                    if '"POST /mpay/api/users/login/qrcode/exchange_token HTTP/1.1" 200' in line:
                        self.check_login_finish_signal.emit(0)
                        runtime_log.info(f"登录成功")
                        return
            timer += 1
            if timer > 30:
                self.check_login_finish_signal.emit(1)
                runtime_log.error(f"登录超时")
                return


if __name__ == '__main__':
    account_manage = AccountManage()
    for account in account_manage.accounts:
        print(account['uuid'])
        print(account['name'])
        print(account['create_time'])
        print(account['last_login_time'])
