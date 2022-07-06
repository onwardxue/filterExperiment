# -*- coding:utf-8 -*-
"""
描述：
作者：Bin bin Xue
日期：2022年04月23日
"""
import random
from PIL import Image
from matplotlib import pyplot as plt

from matplotlib.pyplot import imshow, show
from numpy import array


class AddNoiseToImage():

    def __init__(self, source_image, sigma):
        self.source_image = source_image
        self.sigma = sigma
        self.kind = 3

    def image_dispose(self):
        image_to_array = array(Image.open(self.source_image))

        r, g, b = self.array_to_one(image_to_array)

        self.add_noise_print_image(r, g, b, image_to_array,self.kind)

    def array_to_one(self, high_array):
        r = high_array[:, :, 0].flatten()
        g = high_array[:, :, 1].flatten()
        b = high_array[:, :, 2].flatten()
        return r, g, b

    def add_noise_print_image(self, r, g, b, image_to_array,kind):
        for i in range(image_to_array.shape[0] * image_to_array.shape[1]):
            r[i], g[i], b[i] = self.standrad_random(r[i], g[i], b[i], kind)
        self.regroup(r, g, b, image_to_array)
        imshow(image_to_array)
        self.save_image(image_to_array)
        show()

    # 添加标准正太分布的随机数
    def standrad_random(self, r, g, b, i):
        pr = control_range(int(r) + self.noise(i))
        pg = control_range(int(g) + self.noise(i))
        pb = control_range(int(b) + self.noise(i))

        return pr, pg, pb

    def noise(self,i):
        if(i==1):
            return random.normalvariate(0,self.sigma)
        elif(i==2):
            return random.gauss(0,self.sigma)
        elif(i==3):
            return random.lognormvariate(0,self.sigma)

    def regroup(self, r, g, b, image):
        image[:, :, 0] = r.reshape([image.shape[0], image.shape[1]])
        image[:, :, 1] = g.reshape([image.shape[0], image.shape[1]])
        image[:, :, 2] = b.reshape([image.shape[0], image.shape[1]])

    def save_image(self, image):
        after_image = Image.fromarray(image)
        after_image.save(self.source_image[0:self.source_image.index('.')] + '_' + str(self.kind) + '_' + str(self.sigma) + '.jpg')


def control_range(k):
    if k > 255:
        t = 255
    elif k < 0:
        t = 0
    else:
        t = k
    return t


def plot_image():
    original = str('addNoise/img.jpg')
    img0 = Image.open(original)
    plt.figure(figsize=(30, 20))
    plt.subplot(2, 3, 1)
    plt.title("Original")
    plt.imshow(img0)
    ad = AddNoiseToImage(img0,0)
    for i in range(1, 4, 1):
        plt.subplot(2, 3, i + 1)
        plt.title('sigma = ' + str(i * 10))
        after = 'addNoise/img_' + str(ad.kind)+'_'+str(int(i * 10)) + '.jpg'
        image = Image.open(after)
        plt.imshow(image)
    plt.show()


def main():
    try:
        # source_image = input('请输入需要添加噪声的图片的路径：')
        source_image = 'addNoise/img.jpg'
        # sigma = int(input('请输入sigma值：'))
        i = 1
        for sigma in range(10, 35, 10):
            AN = AddNoiseToImage(source_image, sigma)
            AN.image_dispose()
            print('第' + str(i) + '/3个图片已经输出！')
            i = i + 1
    except IOError:
        print("请重新输入需要处理的图片的正确路径：")
    plot_image()
    print("图片处理完成，退出当前程序！")


if __name__ == '__main__':
    main();
