import logging
import getpass
from apis.components import Components

username = input("请输入用户名： ")
logging.info("here")
password = getpass.getpass("请输入密码： ")
config = {
    "rooturl": "http://nexus3.homelab.com",
    "restapi": "/service/rest/v1",
    "username": username,
    "password": password
}


# 包下载目录
download_dir = r"F:\Software\Linux\package\centos"

# 设置日志
logger = logging.getLogger("nexus3cli")


def main():
    instance = Components(config["rooturl"], config["restapi"], "yum")


if __name__ == "__main__":
    main()