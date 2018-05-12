#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import re
import sys
import json
import plistlib

tile_width = 32 #ширина тайла в клетках в программе, генерирующей json
tile_height = 5 #высота тайла в клетках в программе, генерирующей json
ground_height = 23 #высота самой верхней картинки, никак не участвующей в вычислениях

def metadata():
    static = {
              'machines_normal_speed':0.6,
              'machines_count':1                          
              }
    return static

def machines_start_points():
    static = [
               {
                'position_y':-0.6919999999999999,
                'position_x':0.427
                }
               ]
    return static

#читаем исходный json файл
def readfile(json_file):
    f = file(json_file, 'r')
    content = f.read()        
    f.close()    
    return content

#преобразование json строки в питонный объект
def tojson(filecontent):
    json_objs = json.loads(filecontent)    
    return json_objs

#сохраняем сгенерированный питонный объект в plist
def saveplist(json_file, plist):
    f = open(json_file + '.plist', 'w')
    f.write(plist)
    f.close()

#описание всех имеющихся на карте объектов
def object_types():
    #все типы объектов
    list_objects = ['ground', 'layer', 'goldmine', 'hole', 'rock', 'gold', 'gem', 'drill', 'mushroom', 'worm', 'flashlight', 'bomb', 'wrench', 'items']
    objects = {
               'ground':{},     're_ground': re.compile("ground"),               
               'layer':{},      're_layer': re.compile("layer"),               
               'goldmine':{},   're_goldmine': re.compile("goldmine"),               
               'hole':{},      're_hole': re.compile("hole"),
               'rock':{},      're_rock': re.compile("Rock[1-9]"),
               'gold':{},      're_gold': re.compile("gold(?!mine)"),
               'gem':{},      're_gem': re.compile("gem"),
               'drill':{},      're_drill': re.compile("drill"),
               'mushroom':{},      're_mushroom': re.compile("mushroom"),
               'worm':{},      're_worm': re.compile("worm"),
               'flashlight':{},      're_flashlight': re.compile("flashlight"),
               'bomb':{},      're_bomb': re.compile("bomb"),
               'wrench':{},      're_wrench': re.compile("wrench"),
               'items':{},      're_items': re.compile("hole|Rock[1-9]|gold(?!mine)|gem|drill|mushroom|worm|flashlight|bomb|wrench"),
               }
    
    return {
            'list_objects': list_objects,
            'clean_objects': objects,
            }
    
#сортируем объекты по типам
def object_sorting(pl, list_objects, objects):    
    for one in pl['tilesets']:
        for one_obj in list_objects:            
            if objects['re_'+one_obj].findall(one['name']):
                objects[one_obj][one['firstgid']] = {
                               'firstgid':one['firstgid'],
                               'name':one['name'],
                               'type':objects['re_'+one_obj].findall(one['name'])[0].lower()
                               }
                
    return objects
    
#здесь мы пытаемся достать из огромного одномерного массива-описания ячеек, из файла json, 
#какие тайлы есть на карте и сколько раз они повторяются
def parse_layers(one, objects):
    layers = []
    
    current_tile_type = 0 #тип текущего в цикле тайла
    count_tile_type = 0 #количество повторений текущего тайла в цикле
    num_tiles = 0    #общее количество тайлов
    for i in one['data']:                
        if i != 0:
            num_tiles = num_tiles + 1          
            # если тайл всё ещё тот же самый, добавляем ему счётчик
            if i == current_tile_type:                        
                count_tile_type = count_tile_type + 1
            # если тайл изменился, значит его можно записывать в файл
            elif i != current_tile_type and current_tile_type != 0:        
                layers.append({
                            'type': current_tile_type,
                            'count': count_tile_type,
#                            'name': objects['layer'][current_tile_type]['name']
                            })   
                current_tile_type = i
                count_tile_type = 1
            # это условие нужно, чтоб обработать первый ненулевой тайл
            else:
                current_tile_type = i
                count_tile_type = 1
    
    #добавление последнего слоя таким образом, потому что предыдущий цик кончился, и в условия добавления не зашёл
    layers.append({
                    'type': current_tile_type,
                    'count': count_tile_type,
#                    'name': objects['layer'][current_tile_type]['name']
                    })    
    return {
            'layers': layers,
            'num_tiles': num_tiles
            }

#здесь огромный одномерный массив рабочей области расположения предметов на карте, мы превращаем
#в двумерные массивы, соответствующие тайлам на карте
def items_work_area(tiles, data, tile_width, tile_height, ground_height):
    start_point = tile_width * ground_height
    end_point = start_point + tiles*tile_height*tile_width
    #рабочая область одномерным массивом
    plain_work_area = data[start_point:end_point]
    
    #рабочая область в двумерном моссиве со строкой равной ширене тайла
    work_area = []
    for j in range(0, tiles*tile_height):
        start_str_point = j * tile_width
        end_str_point = (j + 1) * tile_width
        work_area.append(plain_work_area[start_str_point:end_str_point])
        
    #рабочая область с делением на тайлы
    work_area_by_layers = {}
    for k in range(0, tiles):
        start_layer_point = k * tile_height
        end_layer_point = (k + 1) * tile_height
        work_area_by_layers[k] = work_area[start_layer_point:end_layer_point]
        
    return work_area_by_layers

#в раздробленной на слои зоне расположения всяких предметов ищем их, вычисляем координаты и записываем
def parse_items(work_area, tile_width, tile_height, objects):
    items = []
    
    for key, value in work_area.iteritems():
        for i in range(0, tile_height): 
            for j in range(0, tile_width):
                if value[i][j] != 0:    
                    items.append({
                                 'var_x':0,
                                 'var_y':0,
                                 'mean_x':float(j)/float(tile_width),
                                 'mean_y':float(i)/float(tile_height) + key,
                                 'type':objects['items'][value[i][j]]['type'],
#                                     'name': objects['items'][value[i][j]]['name']
                                 })
    return items

#тут то мы и генерируем этот адский плист из не менее адского json файла
def genplist(pl, tile_width, tile_height, ground_height):    
    src_for_plist = {}
    src_for_plist['objects'] = []
    src_for_plist['layers'] = []
    src_for_plist['metadata'] = metadata()
    src_for_plist['machines_start_points'] = machines_start_points()
    
    list_objects = object_types()['list_objects']
    objects = object_types()['clean_objects']
    objects = object_sorting(pl, list_objects, objects)
    
    #парсим слои
    for one in pl['layers']:
        #разбор тайлов слоёв фона        
        if one['name'] == 'layer_layer':
            layers = parse_layers(one, objects)
            num_tiles = layers['num_tiles']
            src_for_plist['layers'] = layers['layers']            
                             
        #разбор предметов раскиданных на карте
        if one['name'] == 'layer_Rock':
            work_area = items_work_area(num_tiles, one['data'], tile_width, tile_height, ground_height)            
            src_for_plist['objects'] = parse_items(work_area, tile_width, tile_height, objects)
    
#    for one_obj in list_objects:
#        print one_obj, '-----', objects[one_obj]
    
    pl = plistlib.writePlistToString(src_for_plist)    
    return pl
    
json_file = sys.argv[1]
filecontent = readfile(json_file)
json_objs = tojson(filecontent)
plist = genplist(json_objs, tile_width, tile_height, ground_height)
saveplist(json_file, plist)
  