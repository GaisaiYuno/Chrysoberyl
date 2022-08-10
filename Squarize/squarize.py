# -*- coding:utf-8 -*-
from PIL import Image
import os


def Square_Generated(read_file):
    image = Image.open(read_file)
    w, h = image.size
    new_image = Image.new('RGB', size=(max(w, h), max(w, h)), color='white')
    length = int(abs(w - h))
    box = ((int)(length / 2), 0) if w < h else (0, (int)(length / 2))
    new_image.paste(image, box)
    new_image = new_image.resize((max(w, h), max(w, h)))
    return new_image


source_path = './'

file_names = os.listdir(source_path)
for i in range(len(file_names)):
    suffix = os.path.splitext(file_names[i])[-1]
    if suffix != ".png" and suffix != ".jpg":
        continue
    img = Square_Generated(source_path + file_names[i])
    os.remove(source_path + file_names[i])
    img.save(save_path + file_names[i], 'PNG')
