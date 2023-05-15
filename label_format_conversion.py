import os
import xml.etree.cElementTree as ET

# 负责将其他格式的标注文件转换为目标格式文件
# 目标格式：csv
# 序号(id)，图片名字（image_id），"[标注框位置（geometry）]"，类别
# 标注框位置格式："[(左上x,左上y),(右上x,右上y),(右下x,右下y),(左下x,左下y)]"


# 从原label转为新label的map
label_convertion_map={'small-vehicle':'smallvehicle',
                      'plane':'plane',
                      'tank':'tank',
                      'helicopter':'helicopter',
}

# 读取一个DOTA_lables格式的txt，返回list
def read_dota_lables(path):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    # 第一行第二行无用，剩下的每一行是一个目标
    lines = lines[2:]
    out_list = []
    for line in lines:
        line = line.split(' ')
        # 把line组成一个元组，放到out_list中
        # 0:8是目标位置，8是类别
        line[8] = line[8].strip().lower()
        line = tuple(line)
        out_list.append(line)
    # 获得path的simple name
    img_id = path.split('/')[-1].replace('txt','png')
    return out_list, img_id

# 解析VOC格式的xml文件，返回list
def read_tank_labels(path):
    tree = ET.parse(path)
    root = tree.getroot()
    filename = root.find('filename').text
    out_list = []
    for object in root.findall('object'):
        cls_name = object.find('name').text.strip().lower()
        # 标注框位置
        xml_box = object.find('bndbox')
        xmin = (float(xml_box.find('xmin').text) - 1)
        ymin= (float(xml_box.find('ymin').text) - 1)
        xmax = (float(xml_box.find('xmax').text) - 1)
        ymax = (float(xml_box.find('ymax').text) - 1)    
        # 把line组成一个元组，放到out_list中
        line = (str(xmin), str(ymin), str(xmax), str(ymin), str(xmax), str(ymax), str(xmin), str(ymax), cls_name)
        out_list.append(line)
    return out_list, filename

        

# main
if __name__ == '__main__':
    # "/home/lth/207_lable/label_format_conversion/DOTA_labels"
    # csv文件
    csv_file = 'new_label.csv'
    # 无效文件
    invalid_file = 'invalid_image.txt'
    # dota文件夹
    dota_path = 'DOTA_labels/'
    # 获得文件夹所有文件名
    dota_files = os.listdir(dota_path)  
    # 排序
    dota_files.sort()
    # tank文件夹
    tank_path = 'Tank_labels/'
    tank_files = os.listdir(tank_path)
    tank_files.sort()

    
    # 确认csv文件是否存在
    if os.path.exists(csv_file):
        os.remove(csv_file)
    # 创建csv文件
    f_csv = open(csv_file, 'w')
    f_csv.write('id,image_id,geometry,class\n')
    id = 1
    invalid_image = []

    # 逐个文件转换
    for data_num, dota_file in enumerate(dota_files): 
        # 打印进度
        print('[%d/%d], 正在处理DOTA labels %s' % (data_num+1, len(dota_files), dota_file))
        # 读取DOTA_lables格式的txt，返回一个list
        dota_list, image_id = read_dota_lables(dota_path + dota_file)
        old_id = id
        # 逐个目标转换
        for dota in dota_list:
            # 标注框位置
            geometry = dota[0:8]
            # 类别
            class_ = dota[8]
            # 转换类别
            if class_ in label_convertion_map:
                class_ = label_convertion_map[class_]
                # 写入csv文件
                # 示例
                # 1,4f833867-273e-4d73-8bc3-cb2d9ceb54ef.jpg,"[(135, 522), (245, 522), (245, 600), (135, 600)]",Airplane
                line = str(id) + ',' + image_id + ',"[' + \
                    "(" + geometry[0] + ',' + geometry[1] + '),' + \
                    "(" + geometry[2] + ',' + geometry[3] + '),' + \
                    "(" + geometry[4] + ',' + geometry[5] + '),' + \
                    "(" + geometry[6] + ',' + geometry[7] + ')' + \
                    ']",' + class_ + '\n'
                f_csv.write(line)
                id = id + 1
        #没有任何有效目标的图像
        if(id == old_id):
            invalid_image.append(image_id)


    for data_num, tank_file in enumerate(tank_files):
        # 打印进度
        print('[%d/%d], 正在处理tank labels %s' % (data_num+1, len(tank_files), tank_file))
        # 读取DOTA_lables格式的txt，返回一个list
        tank_list, image_id = read_tank_labels(tank_path + tank_file)
        old_id = id
        # 逐个目标转换
        for tank in tank_list:
            # 标注框位置
            geometry = tank[0:8]
            # 类别
            class_ = tank[8]
            # 转换类别
            if class_ in label_convertion_map:
                class_ = label_convertion_map[class_]
                # 写入csv文件
                # 示例
                # 1,4f833867-273e-4d73-8bc3-cb2d9ceb54ef.jpg,"[(135, 522), (245, 522), (245, 600), (135, 600)]",Airplane
                line = str(id) + ',' + image_id + ',"[' + \
                    "(" + geometry[0] + ',' + geometry[1] + '),' + \
                    "(" + geometry[2] + ',' + geometry[3] + '),' + \
                    "(" + geometry[4] + ',' + geometry[5] + '),' + \
                    "(" + geometry[6] + ',' + geometry[7] + ')' + \
                    ']",' + class_ + '\n'
                f_csv.write(line)
                id = id + 1
        #没有任何有效目标的图像
        if(id == old_id):
            invalid_image.append(image_id)    
    
    # 关闭csv文件
    f_csv.close()
    print('转换完成')
    # 目标数量
    print('目标数量：', id-1)
    # 无效图像数量
    print('无效图像数量：', len(invalid_image))
    # 无效图像名字
    print('无效图像名字：', invalid_image)
    # 把无效图像名字写入txt文件
    with open(invalid_file, 'w') as f:
        f.write(str(invalid_image))