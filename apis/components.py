from requests import Session
from apis import BaseApi
from requests.auth import HTTPBasicAuth
import os
from tqdm import tqdm
import logging


logger = logging.getLogger("nexus3cli")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Components(BaseApi):
    def __init__(self, baseurl, resturi, apiname):
        super().__init__(baseurl, resturi)
        self.apiname = apiname

    def upload(self, root_path, username, password, repository):
        with Session() as session:
            auth = HTTPBasicAuth(username, password)
            session.auth = auth
            params = {"repository": repository}

            # 计算要上传的文件总数
            total_files = sum([len(files) for r, d, files in os.walk(root_path)])

            # 使用tqdm创建进度条
            with tqdm(total=total_files, desc="Uploading files", unit="file") as pbar:
                for rootpath, _, filelist in os.walk(root_path):
                    for file in filelist:
                        filepath = os.path.join(rootpath, file)
                        directory = os.path.relpath(rootpath, root_path)

                        # 确保文件在操作完成后关闭
                        with open(filepath, 'rb') as filepoint:
                            files = {}
                            if self.apiname == "pypi":
                                files = {"pypi.asset": filepoint}
                            elif self.apiname == "yum":
                                if file.endswith(".rpm"):
                                    files = {
                                        "yum.directory": (None, directory),
                                        "yum.asset.filename": (None, file),
                                        "yum.asset": filepoint
                                    }
                                else:
                                    logger.info(f"Not RPM file, Skipping {file}")
                                    pbar.update(1)
                                    continue

                            response = session.post(self.get_url(self.apiname),
                                                    params=params,
                                                    files=files)

                            if response.status_code > 299:
                                message = "{code}, {reason}, {file}".format(file=filepath,
                                                                            code=response.status_code,
                                                                            reason=response.content.decode("utf-8"))
                                logger.error(message)
                            else:
                                logger.info(f"Successfully uploaded {file}")

                            # 更新进度条
                            pbar.update(1)

    def download(self, package_name, repository, download_dir):
        pass