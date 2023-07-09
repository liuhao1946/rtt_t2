import requests
from tqdm import tqdm

def check_for_updates():
    response = requests.get("https://gitee.com/api/v5/repos/bds123/bds_tool/releases")
    data = response.json()

    # 假设最新版本的发布位于返回列表的第一项（这可能需要根据Gitee的实际行为进行调整）
    latest_release = data[-1]

    print(data[-1])

    latest_version = latest_release['tag_name']

    current_version = "1.0.0"  # 这里应从应用的配置中读取当前版本号

    if latest_version != current_version:
        print("有新版本可用！当前版本：{}，最新版本：{}".format(current_version, latest_version))
        download_url = latest_release['assets'][0]['browser_download_url']
        download_and_install_update(download_url)


def download_and_install_update(url):
    # 请求文件
    response = requests.get(url, stream=True)

    # 获取文件大小
    total_size_in_bytes = int(response.headers.get('Content-Length', 0))
    print("Total file size: {} bytes".format(total_size_in_bytes))

    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    # 下载新版本的msi文件
    with open('update.msi', 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)

    progress_bar.close()

    # 启动安装器
    # os.startfile('update.msi')  # 此方法适用于Windows系统

# check_for_updates()

import os

# 获取当前用户的主目录
home_dir = os.path.expanduser('~')
# 构建下载路径
download_path = os.path.join(home_dir, 'Downloads')

print(download_path)  # 输出：C:\Users\当前用户名\Downloads

