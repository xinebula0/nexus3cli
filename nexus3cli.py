from requests import Session
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import os
import logging
import getpass

config = {
    "rooturl": "http://nexus3.homelab.com",
    "restapi": "/service/rest/v1",
}
# basic configuration from file
params = {"repository": "zwpt-pypi-hosted"}

# interact configuation from user input
config["username"] = input("请输入用户名： ")
config["password"] = getpass.getpass("请输入密码： ")
auth = HTTPBasicAuth(username, password)
session = Session()
session.auth = auth

uri = "/service/rest/v1/components"
url = urljoin(rooturl, uri)

# 包下载目录
download_dir = r"F:\Software\Linux\package\centos"


def download_package_from_nexus(package_name, nexus_url, repository_name, auth, download_dir):
    # 搜索包的URL
    search_url = f"{nexus_url}/service/rest/v1/search/assets?repository={repository_name}&name={package_name}"

    response = requests.get(search_url, auth=auth)

    if response.status_code == 200:
        assets = response.json()['items']
        for asset in assets:
            download_url = asset['downloadUrl']
            filename = asset['path'].split('/')[-1]
            file_path = os.path.join(download_dir, filename)

            with requests.get(download_url, auth=auth, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"Successfully downloaded {filename} to {file_path}")
    else:
        print(f"Failed to search for package {package_name}: {response.status_code} {response.text}")


def main():
    # 创建认证对象
    auth = HTTPBasicAuth(username, password)

    # 要下载的RPM包名称列表
    packages = ["bind-libs-9.11.4-26.P2.el7_9.16.x86_64.rpm", "package2.rpm"]

    for package in packages:
        download_package_from_nexus(package, nexus_url, repository_name, auth, download_dir)


if __name__ == "__main__":
    main()