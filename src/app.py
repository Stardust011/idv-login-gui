import asyncio
import os
import subprocess
import sys
import time
import winreg

import psutil
import py7zr
import win32com.client
from PyQt5.QtCore import QThread, pyqtSignal

from src.config import cfg
from src.dirPrefix import dirPrefix
from src.runtimeLog import runtime_log


# HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store
def read_reg_value():
    # 读取注册表路径下所有值
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store')
    # 找到含有dwrg的键
    game_path = []
    for i in range(1024):
        try:
            subkey = winreg.EnumValue(key, i)
            # print(subkey)
            if 'dwrg.exe' in subkey[0]:
                game_path.append(subkey[0])
                runtime_log.info(f"找到游戏路径: {subkey[0]}")
        except Exception as e:
            if '[WinError 259]' in str(e):
                runtime_log.info("读取注册表完毕")
            else:
                runtime_log.exception(f"读取注册表失败: {e}")
            break
    return game_path


# 创建快捷方式(Lnk)
def create_shortcut(target_path, icon_location=''):
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(os.path.join(cfg.get(cfg.workDir), 'dwrg.lnk'))

    shortcut.Targetpath = target_path
    shortcut.WorkingDirectory = target_path[:-9]
    if icon_location:
        shortcut.IconLocation = icon_location
    shortcut.save()


# # Example usage
# create_shortcut(
#     target_path=r'C:\Path\To\Your\Application.exe',
#     shortcut_path=r'C:\Users\YourUsername\Desktop\YourShortcut.lnk',
#     working_directory=r'C:\Path\To\Your',
#     icon_location=r'C:\Path\To\Your\Application.exe,0'
# )

def start_app_with_explorer(app_path=os.path.join(cfg.get(cfg.workDir), 'dwrg.lnk')):
    try:
        subprocess.Popen(f'explorer.exe "{app_path}"')
        runtime_log.info(f"Opened with explorer.exe")
    except Exception as e:
        runtime_log.exception(f"Error opening application: {e}")


def start_proxy():
    # 清理登录器残存的log文件
    log_path = os.path.join(cfg.get(cfg.workDir), 'log.txt')
    if os.path.exists(log_path):
        os.remove(log_path)
        runtime_log.info(f"清理登录器原有log: {log_path}")

    try:
        login_proxy_path = os.path.join(cfg.get(cfg.workDir), 'idv-login.exe')
        # 检查是否有这个文件
        if not os.path.exists(login_proxy_path):
            runtime_log.warning(f"登录代理文件不存在，解压自带资源")
            archive_path = dirPrefix('assets/idv-login.7z')
            extract_path = cfg.get(cfg.workDir)
            # 解压
            with py7zr.SevenZipFile(archive_path, mode='r') as z:
                z.extractall(path=extract_path)

        # Using shell=True to allow runas command
        login_proxy_log_path = os.path.join(cfg.get(cfg.workDir), 'idv-login-log.txt')
        command = [login_proxy_path,
                   '>', login_proxy_log_path, '2>&1'
                   ]
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True,
                             # text=True,
                             )

        # 输出
        while True:
            time.sleep(0.5)
            with open(login_proxy_log_path, 'r', encoding='gbk') as f:
                line = f.readlines()
                if not line:
                    continue
                if '您可以关闭本工具' in line[-1]:
                    break
                elif 'ERROR' in line[-1]:
                    break
        if '您可以关闭本工具' in line[-1]:
            runtime_log.info(f"启动登录代理进程成功：{p.pid}")
            return True
        elif 'ERROR' in line[-1]:
            runtime_log.error(f"启动登录代理进程失败：{''.join(line)}")
            return False

    except Exception as e:
        runtime_log.exception(f"启动登录代理进程失败: {e}")
        return False


class StartProxyThread(QThread):
    # 建立一个信号槽，执行完毕后发送成功或失败信号
    start_proxy_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        self.start_proxy_signal.emit(start_proxy())
        return


def stop_proxy():
    try:
        # 查找进程列表中是否存在指定名称中含'idv-login'的进程
        # proc_list = []
        for proc in psutil.process_iter():
            if 'idv-login.exe' in proc.name():
                # proc_list.append(proc)
                proc.kill()
                runtime_log.info(f"关闭进程: {proc.name()} {proc.pid}")
        # print(proc_list)
        # # 给启动时间靠后的进程发送关闭信号
        # if proc_list:
        #     proc_list.sort(key=lambda x: x.create_time())
        #     # 发送关闭Ctrl+C信号
        #     print(proc_list)
        #     proc_list[-1].send_signal(CTRL_C_EVENT)
        # proc.terminate()
    except Exception as e:
        runtime_log.exception(f"关闭进程失败: {e}")

    try:
        # 读取host文件
        host_path = r'C:\Windows\System32\drivers\etc\hosts'
        with open(host_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                # 删除host文件中的指定行，含有service.mkey.163.com
                if 'service.mkey.163.com' in line:
                    lines.remove(line)
                    runtime_log.info(f"删除hosts文件中的: {line}")
        # 重新写入host文件
        with open(host_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except Exception as e:
        runtime_log.exception(f"删除hosts条目失败: {e}")

    try:
        # 删除登录器残留log文件
        # 获取本程序运行目录
        current_run_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        log_path = os.path.join(current_run_dir, 'log.txt')
        if os.path.exists(log_path):
            os.remove(log_path)
            runtime_log.info(f"清理登录器原有log: {log_path}")
        # 备份完整log文件
        log_path = os.path.join(cfg.get(cfg.workDir), 'idv-login-log.txt')
        if os.path.exists(log_path):
            if os.path.exists(os.path.join(cfg.get(cfg.workDir), f'idv-login-log-latest.txt')):
                os.remove(os.path.join(cfg.get(cfg.workDir), f'idv-login-log-latest.txt'))
            os.rename(log_path, os.path.join(cfg.get(cfg.workDir), f'idv-login-log-latest.txt'))
            runtime_log.info(f"备份登录器log文件: {log_path}")
    except Exception as e:
        runtime_log.exception(f"删除登录器log文件失败: {e}")


# 示例用法
if __name__ == '__main__':
    # print("Reading registry values...")
    # paths = read_reg_value()
    # print(paths[-1][:-8])
    # create_shortcut(paths[-1])
    #
    # # target_app = r"C:\ProgramData\idv-login\dwrg.lnk"
    # start_app_with_explorer()

    # asyncio.run(start_proxy())
    # stop_proxy()
    # log_path = os.path.join(cfg.get(cfg.workDir), 'log.txt')
    # if os.path.exists(log_path):
    #     with open(log_path, 'r', encoding='utf-8') as f:
    #         line = f.readlines()
    #         print(line[-1])

    # print(p.stdout.readlines())
    pass
