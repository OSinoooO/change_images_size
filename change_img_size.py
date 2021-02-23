import os
import re
import yaml
from PIL import Image


# 读取配置信息
config_path = 'config.yml'
with open(config_path, encoding='utf-8') as f:
    config = yaml.full_load(f.read())

base_img_dir = config['base_img_dir']
mb = int(config['image']['max_size'])
dimensions = config['image']['dimensions']
bg_color_rgb = tuple(eval(config['image']['bg_color_rgb']))


def image_resize(image, width=None, height=None):
    """等比缩放图片"""
    # initialize the dimensions of the image to be resized and
    # grab the image size
    w, h = image.size
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = image.resize(dim, Image.ANTIALIAS)
    return resized


def image_scaner():
    """扫描图片路径"""
    print(f'正在扫描 {base_img_dir} 文件夹下的图片')
    print('*' * 50)
    for root, dirs, files in os.walk(base_img_dir):
        for file in files:
            file_path = os.path.join(root, file)
            for dimension in dimensions:
                x = int(dimension.split(',')[0].strip())
                y = int(dimension.split(',')[1].strip())
                change_image_size(file_path, x, y)


def change_image_size(img_path, x, y):
    """修改图片尺寸"""
    img_name = os.path.basename(img_path)
    if img_name == 'Thumbs.db' or re.findall(r'_\d+_\d+\.', img_name):
        return
    try:
        img = Image.open(img_path)
    except Exception as e:
        print(f'打开图片文件失败({img_name})：{e}')
        return
    org_size = img.size  # 获取图片原始尺寸

    # 调整图片大小
    if org_size[0] >= org_size[1]:
        img1 = image_resize(img, width=x)
        img = Image.new(mode=img1.mode, size=(x, y), color=bg_color_rgb)  # 创建背景色
        img.paste(img1, (0, y // 2 - img1.size[1] // 2))  # 合并图片
    else:
        img1 = image_resize(img, width=y)
        img = Image.new(mode=img1.mode, size=(x, y), color=bg_color_rgb)
        img.paste(img1, (x // 2 - img1.size[0] // 2, 0))
    save_image(img, org_size, img_path, img_name)


def save_image(img, org_size, img_path, img_name, quality=75):
    """保存图片"""
    x, y = img.size
    img_dir = os.path.dirname(img_path)
    img_name_pre = img_name.split('.')[0]
    new_img_name = re.sub(r'.*?\.', f'{img_name_pre}_{x}_{y}.', img_name)
    new_img_path = os.path.join(img_dir, new_img_name)
    img.save(new_img_path, quality=quality)
    o_size = os.path.getsize(new_img_path) / 1024 / 1024  # 图片的物理大小 MB
    if quality <= 0:
        print(f'{new_img_path} ({round(o_size, 2)} MB) 图片质量已降到最低，仍然无法满足图片大小 {mb} MB 限制')
        new_img_name = re.sub(r'.*?\.', f'(该图片超过{mb}MB){img_name_pre}_{x}_{y}.', img_name)
        new_img_path = os.path.join(img_dir, new_img_name)
        img.save(new_img_path)
        return
    if o_size >= mb:
        print(f'{new_img_path} ({round(o_size, 2)} MB) 图片超过 {mb} MB，正在尝试降低图片质量... {quality} -> {quality - 5}')
        save_image(img, org_size, img_path, img_name, quality=quality - 5)
    print(f'{img_path}: {org_size[0]}*{org_size[1]} -> {x}*{y}')
    print('-' * 50)


if __name__ == '__main__':
    image_scaner()
    input('按【Enter】键退出...')
