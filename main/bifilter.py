# -*- coding:utf-8 -*-
"""
描述：
作者：Bin bin Xue
日期：2022年04月24日
"""

from PIL import Image
import matplotlib.pyplot as plt
import math
import copy
import time


class BiFilter:

    def __init__(self, distance_sigma, range_sigma, radius):
        self.distance_sigma = distance_sigma
        self.range_sigma = range_sigma
        self.radius = radius
        self.spatial_weight_table = []
        self.range_weight_table = []

    def calculate_spatial_weight_table(self):
        for en_row in range(-self.radius, self.radius + 1):
            self.spatial_weight_table.append([])
            for en_col in range(-self.radius, self.radius + 1):
                distance = -(en_row ** 2 + en_col ** 2) / (2 * (self.distance_sigma ** 2))
                result = math.exp(distance)
                self.spatial_weight_table[en_row + self.radius].append(result)

    def calculate_range_weight_table(self):
        for en in range(0, 256):
            distance = -(en ** 2) / ((self.range_sigma ** 2) * 2)
            result = math.exp(distance)
            self.range_weight_table.append(result)

    def control_range(self, k):
        if k > 255:
            t = 255
        elif k < 0:
            t = 0
        else:
            t = k
        return t

    def extract(self, image):
        h = image.size[0]
        w = image.size[1]
        return h, w

    def to_pixel(self, pixels, i, j):
        rp = pixels[i, j][0]
        gp = pixels[i, j][1]
        bp = pixels[i, j][2]
        return rp, gp, bp

    def get_pixels(self, row, col, en_row, en_col, pixels):
        row_reset = row + en_row
        col_reset = col + en_col
        r = pixels[row_reset, col_reset][0]
        g = pixels[row_reset, col_reset][1]
        b = pixels[row_reset, col_reset][2]
        return r, g, b

    def convolution(self, radius, row, col, r2, g2, b2, r1, g1, b1):
        r_w = (self.spatial_weight_table[row + radius][col + radius] * self.range_weight_table[(abs(r2 - r1))])
        g_w = (self.spatial_weight_table[row + radius][col + radius] * self.range_weight_table[(abs(g2 - g1))])
        b_w = (self.spatial_weight_table[row + radius][col + radius] * self.range_weight_table[(abs(b2 - b1))])
        return r_w, g_w, b_w

    def Bilateral_Filtering(self, source_image):

        height, width = self.extract(source_image)
        radius = self.radius

        self.calculate_spatial_weight_table()
        self.calculate_range_weight_table()

        pixels = source_image.load()
        initial_data = []
        alter_image = copy.deepcopy()

        r_s = g_s = b_s = 0
        r_w_s = g_w_s = b_w_s = 0
        # 边缘像素不滤波（半径范围外的不进行滤波）
        for row in range(radius, height - radius):
            for col in range(radius, width - radius):
                # 对每个像素进行滤波
                rp, gp, bp = self.to_pixel(pixels, row, col)
                initial_data.append((rp, gp, bp))
                for en_row in range(-radius, radius + 1):
                    for en_col in range(-radius, radius + 1):
                        # 获得模块内的像素
                        rp_2, gp_2, bp_2 = self.get_pixels(row, col, en_row, en_col, pixels)
                        # 卷积计算
                        r_w, g_w, b_w = self.convolution(radius, en_row, en_col, rp_2, gp_2, bp_2, rp, gp, bp)
                        # 求和
                        r_w_s, g_w_s, b_w_s = self.addition(r_w_s, g_w_s, b_w_s, r_w, g_w, b_w)
                        # 鲜求和
                        r_s, g_s, b_s = self.addition2(r_s, g_s, b_s, r_w, g_w, b_w, rp_2, gp_2, bp_2)

                # 归一化过程 floor取最小整
                rp = self.uniform(rp, r_s, r_w_s)
                rp = self.uniform(gp, g_s, g_w_s)
                rp = self.uniform(bp, b_s, b_w_s)

                # 设置像素点(控制值域）
                reset_rgb = (self.control_range(rp), self.control_range(gp), self.control_range(bp))
                # 修改指定位置的像素（像素位置，值）
                alter_image.putpixel((row, col), reset_rgb)
                # 重置RGB各初始值
                r_s = g_s = b_s = 0
                r_w_s = g_w_s = b_w_s = 0
                r_w = g_w = b_w = 0
        # 返回修改后的图像
        return alter_image

    def addition(self, a, b, c, a1, b1, c1):
        return (a + a1), (b + b1), (c + c1)

    def addition2(self, a, b, c, a1, b1, c1, a2, b2, c2):
        return (a + a1 * float(a2)), (b + b1 * float(b2)), (c + c1 * float(c2))

    def uniform(self, rp, r_s, r_w_s):
        rp = int(math.floor(r_s / r_w_s))
        return rp


class Experiment:

    def __init__(self,image_route):
        self.image_route = image_route
        self.length = 25
        self.width = 20
        self.line = 2
        self.row = 2

    def image_process(self):
        # 图片路径转成统一的可用字符串
        img = str(self.image_route)
        # 打开图片
        img0 = Image.open(img)
        # 去掉.jpg，留下前缀名字
        img_name = self.extract(img)
        # 初始化图像
        self.initial_plot(img0)
        # 设置空间域sigma、值域sigma和模块半径
        ds, rs, radius = self.factor_setting()
        # 过滤图片并生成子图
        self.general_subplot(ds, rs, radius, img0, img_name)

    def extract(self, img):
        name = img[0:img.index('.')]
        return name

    def initial_plot(self, src):
        # 指定图像的高和宽
        plt.figure(figsize=(self.length, self.width))
        # 子图划分
        plt.subplot(self.line, self.row, 1)
        # 原始图取标题
        plt.title("SRC", fontsize=20)
        plt.imshow(src)
        plt.axis("off")

    def factor_setting(self):
        ds = 5
        rs = 15
        radius = 3
        return ds, rs, radius

    def general_subplot(self, ds, rs, radius, src, img_name):
        count = 1
        bf = BiFilter(ds, rs, radius)
        aft_image = bf.Bilateral_Filtering(src)
        aft_image.save(img_name + '_' + str(count) + '.jpg')
        print('第' + count + '个图片已完成输出!')
        count += 1
        plt.subplot(self.line, self.row, count)
        plt.title('d=' + ds + ',r=' + rs + ',m=' + radius, fontsize=20)
        plt.imshow(aft_image)
        plt.axis('off')


def main():
    try:
        src = input('请输入要进行处理的图片路径：')
        route = 'biFilter/' + src
        ep = Experiment(route)
        ep.image_process()
        print('程序结束！')

    except IOError:
        print("图像文件路径不正确！")


if __name__ == '__main__':
    main()
