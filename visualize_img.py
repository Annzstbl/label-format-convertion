import os
import cv2

# 将图像和标注可视化





# main
if __name__ == '__main__':
    img_path = 'test_img'
    out_path = 'tmp'
    # 判断out_path是否存在，不存在则创建
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    img_list = os.listdir(img_path)

    csv_file = 'new_label.csv'
    # csv每一行是一个目标
    # 读取csv,输出到以image_id为key的map中,value为list形式
    image_object_map = {}
    with open(csv_file, 'r') as f:
        lines = f.readlines()
        # 分割示例
# 1,P0000.png,"[(2238.0,1791.0),(2254.0,1791.0),(2254.0,1813.0),(2238.0,1813.0)]",smallvehiclesmallvehicle
        # 跳过第一行
        for line in lines:
            line = line.strip()
            line = line.split(',')
            id = line[0]
            if id=='id':
                continue
            image_id = line[1]
            # geometry从 第2个逗号到第10个逗号之间
            geometry = line[2:10]
            geometry[0] = float(geometry[0][3:])
            geometry[1] = float(geometry[1][:-1])
            geometry[2] = float(geometry[2][1:])
            geometry[3] = float(geometry[3][:-1])
            geometry[4] = float(geometry[4][1:])
            geometry[5] = float(geometry[5][:-1])
            geometry[6] = float(geometry[6][1:])
            geometry[7] = float(geometry[7][:-3])
            class_ = line[10]
            
            if image_id not in image_object_map:
                image_object_map[image_id] = []
            image_object_map[image_id].append([id, geometry, class_])
    
    for img_name in img_list:
        img_file_path = os.path.join(img_path, img_name)
        out_file_path = os.path.join(out_path, img_name)
        # 读取图片
        img = cv2.imread(img_file_path)
        # 读取标注
        objects = image_object_map[img_name]
        for object in objects:
            id = object[0]
            geometry = object[1]
            class_ = object[2]
            # 画框
            cv2.rectangle(img, (int(geometry[0]), int(geometry[1])), (int(geometry[4]), int(geometry[5])), (0, 0, 255), 2)
            # 写字
            cv2.putText(img, class_, (int(geometry[0]), int(geometry[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # 保存
        cv2.imwrite(out_file_path, img)
        print('save %s' % out_file_path)
        # break

