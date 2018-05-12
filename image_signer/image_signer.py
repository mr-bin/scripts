#!/usr/bin/python2
# -*- coding: utf-8 -*- 

import os
import string
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#путь к папке с оригинальными картинками
photo_path = "/home/mr_bin/temp/"
font = "/usr/share/fonts/TTF/DroidSans.ttf"
config = "/home/mr_bin/temp/config"
font_size = 200
font_color = (0, 0, 0)
char_colors = {'0': (0, 0, 0),
               '1': (255, 0, 0),
               '2': (0, 255, 0),
               '3': (0, 0, 255),
               }

def load_config(config):
    print "читаем конфиг"
    f = open(config, "r")
    lines = f.readlines()
    file_label = []
    for one in lines:
        file_label.append(one.split("--"))
    return file_label    

#формируем данные для генерации новых картинок
def get_original_image_data(photo_path, labels):
    print 'формируем данные для генерации новых картинок'
    image_data = []
    for filename in os.listdir(photo_path):
        try:
            original_image = Image.open(photo_path + filename)
            region = original_image.crop((0, 0, original_image.size[0], original_image.size[1]))
            labelname = ''
            text_point = ()
            for one_label in labels:
                if one_label[0] == filename:
                    labelname = one_label[1].decode("utf-8").strip()
                    text_color = tuple(int(coord) for coord in one_label[2].strip().split(","))
                
            image_data.append({'filename': filename,
                             'labelname': labelname,
                             'original_image_size': original_image.size,
                             'region': region,
                             'text_color': text_color,
                             })
        except:
            print "возможно " + filename + " не картинка"
    
    return image_data

#размер новой картинки
def new_image_size(original_image_size):
    if original_image_size[0] >= original_image_size[1]:
        image_size = [int((original_image_size[1] + 300) * 1.5), original_image_size[1] + 300]        
    else:
        image_size = [int((original_image_size[1] + 300) / 1.5), original_image_size[1] + 300]
        
    return image_size

#куда мы вставим оригинальную картинку на новом пустом поле
def insert_point_to_new_image(old_size, new_size):
    point = (new_size[0] / 2 - old_size[0] / 2, new_size[1] - old_size[1])
    return point

#формируем данные новых картинок
def create_new_image(original_image_data, font, font_size, font_color):
    print 'формируем данные новых картинок'
    files = []
    font = ImageFont.truetype(font, font_size)

    for one_image in original_image_data:
        try:
            size = new_image_size(one_image['original_image_size'])
            new_image = Image.new("RGB", size, (255, 255, 255))
            draw = ImageDraw.Draw(new_image)
            
            point = insert_point_to_new_image(one_image['original_image_size'], size)
            new_image.paste(one_image['region'], (point[0], point[1], one_image['original_image_size'][0] + point[0], one_image['original_image_size'][1] + point[1]))
            
            start_text_point = (point[0],10)
            
            for i in xrange(0, len(one_image['labelname'])):                
                draw.text(start_text_point, one_image['labelname'][i], font_color[str(one_image['text_color'][i])], font=font)
                (width, height) = font.getsize(one_image['labelname'][i])
                start_text_point = (start_text_point[0] + width, 10)
                
            draw = ImageDraw.Draw(new_image)
                 
            files.append((one_image['filename'], new_image))
        except:
            print "возможно картинки " + one_image['filename'] + " нет в конфиге"
        
    return files

#сохраняем в файлы
def new_image_saver(photo_path, new_images):
    print 'сохраняем картинки в файлы'
    for image in new_images:
        image[1].save(photo_path + "/n_" + image[0] + ".jpg")
 
labels = load_config(config)
original_image_data = get_original_image_data(photo_path, labels)
new_images = create_new_image(original_image_data, font, font_size, char_colors)
new_image_saver(photo_path, new_images)