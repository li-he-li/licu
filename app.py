import os
import numpy as np  # 用于处理数组和矩阵
import cv2  # 用于处理图像
import random  # 用于生成随机颜色
from sklearn.cluster import KMeans  # 用于聚类分析
from flask import Flask, render_template, request, jsonify  # 用于构建Web应用
from werkzeug.utils import secure_filename  # 用于确保上传文件名的安全性

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# 生成5个随机颜色
def generate_random_colors():
    colors = [] # 初始化一个空列表，用于存储随机颜色
    
    # 循环5次，生成5个随机颜色
    for _ in range(5):
        # 对于红色、绿色和蓝色分量，分别生成一个随机整数，范围在0到255之间（包括0和255）
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        # 使用字符串格式化将红色、绿色和蓝色分量组合成一个十六进制颜色字符串
        color = '#%02x%02x%02x' % (r, g, b)
        
        # 将生成的颜色添加到颜色列表中
        colors.append(color)
    
    # 返回包含5个随机颜色的列表
    return colors

# 提取图像的主要颜色
def extract_colors(image, n_colors=5):
    # 将输入图像reshape为二维数组，其中每行包含一个像素的三个颜色分量（红、绿、蓝）
    image = image.reshape(-1, 3)
    
    # 使用KMeans算法，初始化一个聚类器，设置聚类数量为n_colors（默认为5）
    kmeans = KMeans(n_clusters=n_colors,n_init='auto')
    
    # 使用KMeans聚类算法对图像的颜色进行聚类，找到代表性颜色
    kmeans.fit(image)
    
    # 返回聚类后的颜色中心，即代表性颜色
    return kmeans.cluster_centers_

# 主页路由
@app.route('/')
def home():
    return render_template('home.html')

# 定义路由和处理函数，响应POST请求
# 当客户端向`/random_palette`发送POST请求时，此处理函数将被调用
@app.route('/random_palette', methods=['POST'])
def random_palette():
    # 调用generate_random_colors生成随机颜色
    colors = generate_random_colors()
    # 使用jsonify将颜色列表转换为JSON格式，并作为响应返回
    return jsonify(colors)

# 上传图像并提取颜色路由
@app.route('/upload_image', methods=['POST'])
def upload_image():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    # 获取文件对象
    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    # 使用secure_filename确保文件名的安全性
    filename = secure_filename(file.filename)

    # 构建文件保存路径
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # 保存上传的文件
    file.save(filepath)

    # 使用OpenCV读取图像文件，并将BGR颜色空间转换为RGB颜色空间
    # 读取图像，参数为图像文件路径
    image = cv2.imread(filepath)  
    # 将 BGR 颜色空间转换为 RGB 颜色空间
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  


    # ------------------------------------------------------------------------------
    # 从请求中获取长方形框的坐标
    crop_box_coords = request.form.get('cropBoxCoords')
    print("crop_box_coords",crop_box_coords)

    # 如果提供了框的坐标，对图像进行裁剪
    if crop_box_coords:
        x, y, width, height = [int(coord) for coord in crop_box_coords.split(',')]
        print("选中的尺寸是: ",x,y,width,height)
        image = image = image[y:y + height, x:x + width] # 从原image中截取左上角是(x,y)，宽度为width，高度为height的区域

    # 调用extract_colors函数提取图像的代表性颜色
    palette = extract_colors(image)
    # ------------------------------------------------------------------------------


    # 调用extract_colors函数提取图像的代表性颜色
    palette = extract_colors(image)

    # 将颜色调色板转换为JavaScript代码可用的格式
    palette_for_js = ["#%02x%02x%02x" % (int(color[0]), int(color[1]), int(color[2])) for color in palette]

    # 返回JSON格式的颜色调色板
    return jsonify(palette_for_js)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5001)
    # app.run(debug=True)