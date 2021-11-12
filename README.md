# markdown_oss
提供图片压缩、自动上传到阿里云oss的脚本
## 使用
### 简单使用
会将origin_file_name文件自动转换为webp，并存储到origin_file_name的文件夹
```shell
python3 image_convert.py --path <origin_file_name>
```
### 完整参数
```shell
python3 image_convert.py --format avif --resize 1200 --oss_folder <oss_folder_name> --path <origin_file_name>
```
### 参数说明

1. --format，目标格式，默认webp，支持webp、avif、heic、heif，其实支持各种格式，我懒得写。
如果图片本身已经是webp、avif、heic、heif，将不做转换
2. --resize，最小尺寸，取图片长宽，并自动压缩到resize的值，如不传入，将不做压缩
3. --path，原始文件路径，如果传的是文件夹，将会遍历文件夹下的所有图片并全部压缩。注意：不会遍历子目录
4. --oss_folder，指定上传的阿里云oss路径，不传这个参数，将不会上传oss，注意：oss的bucket已经在脚本里指定了，你可以自己修改脚本

另外，imagemagic本身支持大量的压缩优化定义，可以参考：<https://b.alnk.top/2016-03-23_imagemagick_compress_image/>

## 准备工作
### pip
pip使用到了Pillow和filetype
```shell
pip3 install Pillow
pip3 install filetype
```
### 图片压缩ImageMagic
使用到了ImageMagic：<https://imagemagick.org/script/download.php>
```shell
brew install ghostscript
brew install imagemagick
```

## oss
如果你需要上传到oss，你需要安装工具，并将参数替换到本脚本里
### 阿里云oss
命令行工具：<https://help.aliyun.com/document_detail/120075.html>
### 脚本参数替换
目标命令类似于：
```shell
echo y | /usr/local/bin/ossutil64 -c /opt/local/oss/config-alnk cp -r  /tmp/imagemagic/mydoc/image_4.avif oss://my_bucket/mydoc/
```
上面的命令拆解后，参数如下：
```python
"""
oss的bucket
"""
env_oss_bucket="my_bucket"
"""
oss上传时的路径
"""
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
```
