import datetime
import getopt
import json
import logging
import multiprocessing
import os
import subprocess
import sys
import traceback
import typing
from multiprocessing import pool

import filetype
from PIL import Image

logging.basicConfig(level=logging.INFO)
support_target_format = ["webp", "avif", "heif", "heic"]


class ImageDTO(json.JSONEncoder):
    """
    图片信息的模型;
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

    def __str__(self):
        fields = ['{}={!r}'.format(k, v)
                  for k, v in self.__dict__.items() if not k.startswith('_')]
        return '{}({})'.format(self.__class__.__name__, ','.join(fields))

    """
    源文件路径
    """
    origin_file_path: str = None
    """
    目标文件路径
    """
    target_save_path: str = None
    """
    需要调整的尺寸的语句，类似：-resize 80%
    """
    resize_phrase: str = None
    """
    上传到OSS的文件夹名称
    """
    oss_folder: str = None
    """
    oss根目录，参见env_oss_upload_path
    """
    oss_root: str = None


def make_dir_safe(file_path):
    """
    工具方法：写文件时，如果关联的目录不存在，则进行创建
    :param file_path:文件路径或者文件夹路径
    :return:
    """

    if not file_path or file_path.strip() == "":
        return
    if file_path.endswith("/"):
        if not os.path.exists(file_path):
            os.makedirs(file_path)
    else:
        folder_path = file_path[0:file_path.rfind('/') + 1]
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def process_to_webp(file_info: ImageDTO):
    """
    转换为webp，默认quality 85%比较均衡
    """
    target_command = f"""magick {file_info.origin_file_path} {file_info.resize_phrase} -quality 85% {file_info.target_save_path}"""
    logging.info(target_command)
    subprocess.call([target_command], shell=True)


def process_to_avif(file_info: ImageDTO):
    target_command = f"""magick {file_info.origin_file_path} {file_info.resize_phrase} {file_info.target_save_path}"""
    logging.info(target_command)
    subprocess.call([target_command], shell=True)


def process_to_heif(file_info: ImageDTO):
    target_command = f"""magick {file_info.origin_file_path} {file_info.resize_phrase} {file_info.target_save_path}"""
    logging.info(target_command)
    subprocess.call([target_command], shell=True)


def process_to_heic(file_info: ImageDTO):
    target_command = f"""magick {file_info.origin_file_path} {file_info.resize_phrase} {file_info.target_save_path}"""
    logging.info(target_command)
    subprocess.call([target_command], shell=True)


def upload_to_oss(file_info: ImageDTO):
    """
    上传到OSS
    """
    target_command = f"""echo y | {env_oss_shell} -c {env_oss_shell_config} cp -r  {file_info.target_save_path} {file_info.oss_root}{file_info.oss_folder}/"""
    logging.info(target_command)
    subprocess.call([target_command], shell=True)


def get_files(file_path: str = "") -> typing.List[str]:
    """
    支持传入文件或者文件夹
    """
    if os.path.isfile(file_path):
        file_list: typing.List[str] = []
        tmp_file_name = file_path[file_path.rfind("/") + 1:len(file_path)]
        file_path = file_path[0:file_path.rfind("/") + 1]
        file_list.append(tmp_file_name)
    else:
        if not file_path.endswith("/"):
            file_path = f"{file_path}/"
        file_list = os.listdir(file_path)
    image_list: typing.List[str] = []
    for temp in file_list:
        tmp_file = f"{file_path}{temp}"
        if filetype.is_image(tmp_file):
            """
            提取文件格式，判断是否是图片，是否是支持的格式，如果已经是webp等高压缩格式，将不再进行转换
            """
            if temp.__contains__(".") and temp.rfind(".") < len(temp):
                file_format = temp[temp.rfind(".") + 1:temp.__len__()]
                if file_format not in support_target_format:
                    image_list.append(tmp_file)
                else:
                    logging.info(f"此图片不需要转换格式：{tmp_file}")
            else:
                logging.info(f"文件名不正确：{tmp_file}")
        else:
            logging.info(f"此文件不是图片：{tmp_file}")
    return image_list


def start_convert(file_info: ImageDTO):
    try:
        if file_info.target_save_path.endswith("webp"):
            process_to_webp(file_info=file_info)
        elif file_info.target_save_path.endswith("avif"):
            process_to_avif(file_info=file_info)
        elif file_info.target_save_path.endswith("heif"):
            process_to_heif(file_info=file_info)
        elif file_info.target_save_path.endswith("heic"):
            process_to_heic(file_info=file_info)
        """
        如果指定了oss路径，将开始上传文件到oss
        """
        if file_info.oss_folder and file_info.oss_folder is not None and len(file_info.oss_folder) > 0:
            upload_to_oss(file_info=file_info)
            logging.info(
                f"""oss: {env_oss_full_path}{file_info.oss_folder}/{file_info.target_save_path[file_info.target_save_path.rfind("/") + 1:len(file_info.target_save_path)]}""")
    except Exception as e:
        print(traceback.format_exc())


def start_work():
    try:
        logging.info(f"仅支持转为如下格式 {support_target_format}")
        job_time_start = datetime.datetime.now()
        # 获取文件列表
        img_list = get_files(file_path=param_path)
        if img_list and img_list.__len__() > 0:
            my_pool = multiprocessing.pool.Pool(6)
            for tmp_file in img_list:
                tmp_file_info: ImageDTO = ImageDTO()
                """
                转换后的图片默认存储到源文件夹，如果要求上传到oss，则存储到tmp文件夹
                """
                if param_oss_folder and param_oss_folder is not None and len(param_oss_folder) > 0:
                    target_file_name = f"""/tmp/imagemagic/{param_oss_folder}/{tmp_file[tmp_file.rfind("/") + 1:tmp_file.rfind('.')]}.{param_format}"""
                    tmp_file_info.oss_folder = param_oss_folder
                    tmp_file_info.oss_root = env_oss_upload_path
                else:
                    target_file_name = f"{tmp_file[0:tmp_file.rfind('.')]}.{param_format}"
                make_dir_safe(file_path=target_file_name)
                tmp_file_info.origin_file_path = tmp_file
                tmp_file_info.target_save_path = target_file_name
                tmp_file_info.resize_phrase = ""
                """
                如果指定了尺寸，这里计算尺寸百分比
                """
                if param_resize and param_resize > 0:
                    tmp_img_object = Image.open(tmp_file)
                    tmp_img_min = min(tmp_img_object.width, tmp_img_object.height)
                    tmp_img_object.close()
                    if tmp_img_min > param_resize:
                        scale = int(round(param_resize / tmp_img_min, 2) * 100)
                        tmp_file_info.resize_phrase = f" -resize {scale}%"
                my_pool.apply_async(func=start_convert, args=(tmp_file_info,))
            my_pool.close()
            my_pool.join()
            job_time_end = datetime.datetime.now()
            job_total_costs = job_time_end - job_time_start
            logging.info(f"总耗时 {job_total_costs}")
        else:
            logging.info(f"未找到图片")
    except Exception as e:
        print(traceback.format_exc())

"""
oss的存储路径
"""
env_oss_bucket="my_bucket"
env_oss_upload_path=f"oss://{env_oss_bucket}/"
"""
oss的公网域名
"""
env_oss_full_path=f"https://{env_oss_bucket}.oss-cn-hangzhou.aliyuncs.com/"
"""
oss命令的完整路径和配置文件所在地
"""
env_oss_shell="/usr/local/bin/ossutil64"
"""
oss需要读取密钥，请将密钥存储到你指定的目录
"""
env_oss_shell_config="/opt/local/oss/config-file"
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:f:s:u:",
                                   ["path=", "format=", "resize=", "oss_folder="])
    except getopt.GetoptError:
        logging.info(traceback.format_exc())
        sys.exit(2)
    param_path: str = ""
    param_format: str = "webp"
    param_resize: int = 0
    param_oss_folder: str = None
    for opt, arg in opts:
        if opt in ("-p", "--path"):
            param_path = arg
        elif opt in ("-f", "--format"):
            param_format = arg
        elif opt in ("-s", "--resize"):
            param_resize = int(arg)
        elif opt in ("-u", "--oss_folder"):
            param_oss_folder = arg
    if param_format.__contains__("."):
        param_format = param_format.replace(".", "")
    if param_format not in support_target_format:
        logging.error(f"仅支持转为如下格式 {support_target_format}")
        exit()
    start_work()
    exit(0)
