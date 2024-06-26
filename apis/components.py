from requests import Session
from apis import BaseApi
from requests.auth import HTTPBasicAuth
import os
from tqdm import tqdm
import logging
from pathlib import Path


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
            total_success = 0
            total_failure = 0
            filenames = list()

            # 使用tqdm创建进度条
            with tqdm(total=total_files, desc="Uploading files", unit="file") as pbar:
                for rootpath, _, filelist in os.walk(root_path):
                    for file in filelist:
                        filepath = os.path.join(rootpath, file)

                        # 确保文件在操作完成后关闭
                        with open(filepath, 'rb') as filepoint:
                            files = {}
                            if self.apiname == "pypi":
                                files = {"pypi.asset": filepoint}
                            elif self.apiname == "yum":
                                # 生成yum仓库目录
                                directory = Path(rootpath).relative_to(Path(root_path))
                                directory = (Path("/") / directory).as_posix()

                                if file.endswith(".rpm"):
                                    files = {
                                        "yum.directory": (None, directory),
                                        "yum.asset.filename": (None, file),
                                        "yum.asset": filepoint
                                    }
                                else:
                                    logger.warning(f"Not RPM file, Skipping {file}")
                                    total_failure += 1
                                    filenames.append(("{:<40}".format(file), "Format Error"))
                                    pbar.update(1)
                                    continue

                            response = session.post(self.get_url("components"),
                                                    params=params,
                                                    files=files, verify=False)
                            if response.status_code > 299:
                                message = "{code}, {reason}, {file}".format(file=filepath,
                                                                            code=response.status_code,
                                                                            reason=response.content.decode("utf-8"))
                                logger.warning(message)
                                total_failure += 1
                                filenames.append(("{:<40}".format(file), "HTTP code: " + str(response.status_code)))
                            else:
                                total_success += 1
                                logger.debug(f"Successfully uploaded {file}")

                            pbar.update(1)

        print(f"Total files: {total_files}    Success: {total_success}    Failure: {total_failure}")
        if filenames:
            print("\nDetail Report")
            print("=".rjust(60, "="))
            for item in filenames:
                print(item[0], item[1])

    def download(self, download_dir, username, password, repository):
        with Session() as session:
            auth = HTTPBasicAuth(username, password)
            session.auth = auth
            params = {"repository": repository}
            components = []
            continuation_token = None

            while True:
                if continuation_token:
                    params["continuationToken"] = continuation_token
                response = session.get(self.get_url("components"), params=params)
                response.raise_for_status()
                data = response.json()
                components.extend(data['items'])
                continuation_token = data.get('continuationToken')
                if not continuation_token:
                    break

            for component in components:
                for asset in component['assets']:
                    asset_url = asset['downloadUrl']
                    rawpath = Path(asset['path'])
                    file_name = rawpath.name
                    if self.apiname == "yum":
                        file_path = Path(download_dir) / rawpath.parent
                        absfile = Path(download_dir) / rawpath
                        file_path.mkdir(parents=True, exist_ok=True)
                    elif self.apiname == "pypi":
                        absfile = Path(download_dir) / file_name
                    response = session.get(asset_url, stream=True)
                    response.raise_for_status()

                    total_size = int(response.headers.get('content-length', 0))
                    with open(absfile, "wb") as file, tqdm(
                        desc=file_name,
                        total=total_size,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                            bar.update(len(chunk))
