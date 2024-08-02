import os
import sys


def dirPrefix(dir):
    # 检查是否在临时文件夹
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = './'
    return os.path.join(bundle_dir, dir)
