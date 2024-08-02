import os

from qfluentwidgets import QConfig, ConfigItem, qconfig, BoolValidator

from src.runtimeLog import runtime_log


# class MvQuality(Enum):
#     """ MV quality enumeration class """
#
#     FULL_HD = "Full HD"
#     HD = "HD"
#     SD = "SD"
#     LD = "LD"
#
#     @staticmethod
#     def values():
#         return [q.value for q in MvQuality]


class MyConfig(QConfig):
    """ Config of application """
    # # main window
    # enableAcrylic = ConfigItem("MainWindow", "EnableAcrylic", False, BoolValidator())
    # playBarColor = ColorConfigItem("MainWindow", "PlayBarColor", "#225C7F")
    # themeMode = OptionsConfigItem("MainWindow", "ThemeMode", "Light", OptionsValidator(["Light", "Dark", "Auto"]), restart=True)
    # recentPlaysNumber = RangeConfigItem("MainWindow", "RecentPlayNumbers", 300, RangeValidator(10, 300))
    #
    # # online
    # onlineMvQuality = OptionsConfigItem("Online", "MvQuality", MvQuality.FULL_HD, OptionsValidator(MvQuality), EnumSerializer(MvQuality))

    # main
    workDir = ConfigItem("Main", "WorkDir", os.path.join(os.environ["PROGRAMDATA"], "idv-login"))

    # Login
    autoLogin = ConfigItem("Login", "AutoLogin", False, BoolValidator())


# 创建配置实例并使用配置文件来初始化它
cfg = MyConfig()
path = os.path.join(os.environ["PROGRAMDATA"], "idv-login/guiConfig")
qconfig.load(os.path.join(path, 'config.json'), cfg)
runtime_log.info(f"配置文件已加载")
# cfg.set(cfg.autoLogin, True)
# print(cfg.get(cfg.autoLogin))
