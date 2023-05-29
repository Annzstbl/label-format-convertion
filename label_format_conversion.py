import os
import xml.etree.cElementTree as ET

# 负责将其他格式的标注文件转换为目标格式文件
# 目标格式：csv
# 序号(id)，图片名字（image_id），"[标注框位置（geometry）]"，类别
# 标注框位置格式："[(左上x,左上y),(右上x,右上y),(右下x,右下y),(左下x,左下y)]"


# 从原label转为新label的map
# 不在次行列的类别将被忽略
label_convertion_map={'small-vehicle':'smallvehicle',
                      'plane':'plane',
                      'tank':'tank',
                      'helicopter':'helicopter',
                      'bridge':'bridge',
                      'airport runway':'airportrunway',
}

# 读取一个DOTA_lables格式的txt，返回list
def read_dota_labels(path):
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
        # line的8个元素(x1,y1, x2,y2, x3,y3, x4,y4)中挑出x_min,x_max,y_min,y_max
        # 之后按照左上，右上，右下，左下的顺序排列
        x_min = min(float(line[0]), float(line[2]), float(line[4]), float(line[6]))
        x_max = max(float(line[0]), float(line[2]), float(line[4]), float(line[6]))
        y_min = min(float(line[1]), float(line[3]), float(line[5]), float(line[7]))
        y_max = max(float(line[1]), float(line[3]), float(line[5]), float(line[7]))
        line = (str(x_min), str(y_min), str(x_max), str(y_min), str(x_max), str(y_max), str(x_min), str(y_max), line[8])
        out_list.append(line)
    # 获得path的simple name
    img_id = path.split('/')[-1].replace('txt','png')
    return out_list, img_id

# 解析VOC格式的xml文件，返回list
def read_tank_labels(path):
    tree = ET.parse(path)
    root = tree.getroot()
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
    img_id = path.split('/')[-1].replace('xml','jpg')
    return out_list, img_id

# 解析fair1m数据集的xml文件，返回list
def read_fair1m_labels(path):
    tree = ET.parse(path)
    root = tree.getroot()
    out_list = []
    objects = root.find('objects')
    for object in objects.findall('object'):
        cls_name = object.find('possibleresult').find('name').text.strip().lower()
        # 标注框位置
        xml_boxs = object.find('points')
        xmin = None
        ymin = None
        xmax = None
        ymax = None
        for xmlbox in xml_boxs.findall('point'):
            point = xmlbox.text
            x, y = point.split(',')
            x = float(x)
            y = float(y)
            if xmin is None:
                xmin = x
                ymin = y
                xmax = x
                ymax = y
            else:
                xmin = min(xmin, x)
                ymin = min(ymin, y)
                xmax = max(xmax, x)
                ymax = max(ymax, y)
        # 把line组成一个元组，放到out_list中
        line = (str(xmin), str(ymin), str(xmax), str(ymin), str(xmax), str(ymax), str(xmin), str(ymax), cls_name)

        out_list.append(line)
    img_id = path.split('/')[-1].replace('xml','tif')
    return out_list, img_id

# 解析VOC格式的xml文件，返回list
def read_runway_labels(path):
    tree = ET.parse(path)
    root = tree.getroot()
    out_list = []
    filename = root.find('filename').text
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
    img_id = path.split('/')[-1].replace('xml','jpg')
    return out_list, filename

def conversion(src_dir, csv_file, read_labels, instance_num, new_csv_file=False):
    if os.path.exists(csv_file) and not new_csv_file:
        f_csv = open(csv_file, 'a')
    else:
        f_csv = open(csv_file, 'w')
        f_csv.write('id,image_id,geometry,class\n')

    #srcdir的simple name
    src_dir_simplename = src_dir.split('/')[-2]
    invalid_image = []

    src_files = os.listdir(src_dir)
    src_files.sort()

    for order, file in enumerate(src_files):
        #打印进度
        print('[%d/%d], 正在处理%s 文件 %s' % (order+1, len(src_files), src_dir_simplename, file ))
        
        valid_img = False
        # 读取标签
        label_list, img_id = read_labels(src_dir + file)
        # 写入csv文件
        for label in label_list:
            geometry = label[0:8]
            class_ = label[8]
            if class_ in label_convertion_map:
                class_ = label_convertion_map[class_]
                line = str(instance_num) + ',' + img_id + ',"[' + \
                        "(" + geometry[0] + ',' + geometry[1] + '),' + \
                        "(" + geometry[2] + ',' + geometry[3] + '),' + \
                        "(" + geometry[4] + ',' + geometry[5] + '),' + \
                        "(" + geometry[6] + ',' + geometry[7] + ')' + \
                        ']",' + class_ + '\n'   
                instance_num = instance_num + 1
                valid_img = True
                f_csv.write(line)
        if not valid_img:
            invalid_image.append(img_id)

    f_csv.close()
            
    return instance_num, invalid_image

    

# main
def main_conversion():
    # csv文件
    csv_file = 'new_label.csv'
    # 无效文件
    invalid_file = 'invalid_image.txt'
    # dota文件夹
    dota_path = 'DOTA_labels/'
    # tank文件夹
    tank_path = 'Tank_labels/'
    # fair1m_labels
    fair1m_path = 'FAIR1M_labels/'
    # runway labels
    runway_path = 'runway_labels/'

    instance_num = 1
    invalid_image = []
    instance_num , tmp_invalid_image = conversion(dota_path, csv_file, read_dota_labels, instance_num, True)
    invalid_image.extend(tmp_invalid_image)
    instance_num,  tmp_invalid_image = conversion(tank_path, csv_file, read_tank_labels, instance_num)
    invalid_image.extend(tmp_invalid_image)
    instance_num, tmp_invalid_image = conversion(fair1m_path, csv_file, read_fair1m_labels, instance_num)
    invalid_image.extend(tmp_invalid_image)
    
    csv_file = 'new_label_runway.csv'
    instance_num = 1
    instance_num, tmp_invalid_image = conversion(runway_path, csv_file, read_runway_labels, instance_num)
    invalid_image.extend(tmp_invalid_image)


    print('转换完成')
    # 目标数量
    print('目标数量：', instance_num-1)
    # 无效图像数量
    print('无效图像数量：', len(invalid_image))
    # 无效图像名字
    print('无效图像名字：', invalid_image)
    # 把无效图像名字写入txt文件
    with open(invalid_file, 'w') as f:
        f.write(str(invalid_image))

def show_label():
    # fair1m_lables
    fair1m_path = 'FAIR1M_labels/'
    fair1m_files = os.listdir(fair1m_path)
    fair1m_files.sort()
    # 创建一个class的集合
    class_set = set()
    for data_num, fair1m_file in enumerate(fair1m_files):
        # 打印进度
        print('[%d/%d], 正在处理fair1m labels %s' % (data_num+1, len(fair1m_files), fair1m_file))
        # 读取DOTA_lables格式的txt，返回一个list
        object_list, image_id = read_fair1m_labels(fair1m_path + fair1m_file)
        old_id = id
        # 逐个目标转换
        for fair1m_object in object_list:
            class_ = fair1m_object[8]
            print(class_)
            class_set.add(class_)
    # 输出class_set
    print(class_set)

if __name__ == '__main__':
    main_conversion()
    # show_label()