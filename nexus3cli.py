import logging
import getpass
import argparse
from apis.components import Components


logger = logging.getLogger("nexus3cli")
config = {
    "rooturl": "http://nexus3.homelab.com",
    "restapi": "/service/rest/v1"
}


def main():
    parser = argparse.ArgumentParser(description="Download or upload packages using yum or pypi.")
    parser.add_argument('--cacert', required=False, metavar='cacert', help="Path to the certificate file")
    subparsers = parser.add_subparsers(dest='action', required=True, help="Action to perform")

    # 下载子命令
    download_parser = subparsers.add_parser('download', help="Download packages")
    download_parser.add_argument('target', choices=['yum', 'pypi'], help="Target to download from")
    download_parser.add_argument('--local-path',
                                 required=False,
                                 help="Local path to save the downloaded files")
    download_parser.add_argument('-r', '--repository',
                                 required=True,
                                 help="Name of the repository to download")

    # 上传子命令
    upload_parser = subparsers.add_parser('upload', help="Upload packages")
    upload_parser.add_argument('target', choices=['yum', 'pypi'], help="Target to upload to")
    upload_parser.add_argument('--local-path', required=False, help="Local path of the files to upload")
    upload_parser.add_argument('-d', '--directory', required=False,
                               help="Directory in repository to upload to")
    upload_parser.add_argument('-r', '--repository',
                               required=True,
                               help="Name of the repository to upload to")

    args = parser.parse_args()
    # 根据动作调用相应的函数
    username = input("请输入用户名： ")
    password = getpass.getpass("请输入密码： ")
    if args.action == 'download':
        nexus = Components(config["rooturl"], config["restapi"], args.target)
        nexus.download(args.local_path, username, password, args.repository)
    elif args.action == 'upload':
        nexus = Components(config["rooturl"], config["restapi"], args.target)
        nexus.upload(args.local_path, username, password)


if __name__ == "__main__":
    main()