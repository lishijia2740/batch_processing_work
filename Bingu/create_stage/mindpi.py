import os
import numpy as np
from PIL import Image
import cv2
from matplotlib import pyplot as plt


# 寻找最小坐标
def matdistance(*discance):
    price = discance[0]
    # print(discance)
    mindistance = price[0]
    matdistance = price[0]
    # print(price[0])
    matprofit = 0
    w = len(price)
    for i in range(w):
        if price[i] != 0:
            if price[i] < mindistance or price[i] == mindistance:
                mindistance = price[i]
                # print(mindistance)
            if price[i] > matdistance or price[i] == matdistance:
                matdistance = price[i]

    print("最低点纵坐标", mindistance)
    print("最高点纵坐标", matdistance)
    matprofit = matdistance - mindistance

    return matprofit


# 遍历全部图像，并记录像素为（0，0，0）点的坐标
def cxsearch(image):
    k = 0
    height = image.shape[0]
    print("图像高", height)
    width = image.shape[1]
    print("图像宽", width)
    x = [0] * 5000
    for i in range(height):  # 遍历图像的高
        for j in range(width):  # 遍历图像的宽
            pixel = image[i, j]  # 读取该点的像素值
            if all(pixel == (0, 0, 0)):
                x[k] = i  # 存取像素点是黑色的的纵坐标

                # print(x[k])
                k += 1
    return x


image = cv2.imread("test3.jpg", cv2.IMREAD_COLOR)  # 读入图片
a = image.shape[0]  # 图片的高
b = image.shape[1]  # 图片的宽
# print(a)
# print(b)
# 将图片分为两部分
dis_h = a
dis_w = int(b / 2)
sub1 = image[1:dis_h, 1:dis_w]  # 第一心音
sub2 = image[1:dis_h, dis_w::]  # 第二心音图
dis_hh = int(506 / 2)
sub3 = image[1:dis_hh, :]
sub4 = image[dis_hh::, :]

z1 = matdistance(cxsearch(sub1))  # 求取第一心音的最大幅值
z2 = matdistance(cxsearch(sub2))  # 求取第二心音的最大幅值
z3 = matdistance(cxsearch(sub3))  # 求取第二心音的最大幅值
z4 = matdistance(cxsearch(sub4))  # 求取第二心音的最大幅值
# print("第一最大幅值", z1)
# print("第二最大幅值", z2)

cv2.namedWindow("orient", 0)  # 显示未分割的原始图
cv2.resizeWindow("orient", 640, 480)
cv2.imshow("orient", image)

cv2.namedWindow("orient1", 0)  # 显示分割的子图1
cv2.resizeWindow("orient1", 640, 480)
cv2.imshow("orient1", sub1)

cv2.namedWindow("orient2", 0)  # 显示分割的子图2
cv2.resizeWindow("orient2", 640, 480)
cv2.imshow("orient2", sub2)

cv2.namedWindow("orient3", 0)  # 显示分割的子图1
cv2.resizeWindow("orient3", 640, 480)
cv2.imshow("orient3", sub3)

cv2.namedWindow("orient4", 0)  # 显示分割的子图2
cv2.resizeWindow("orient4", 640, 480)
cv2.imshow("orient4", sub4)
cv2.imwrite('test4.jpg', sub4)
cv2.waitKey(0)
