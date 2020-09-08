import cv2 as cv
import numpy as np


def build_image():
    image = np.random.randint(10, 99, size=[5, 5], dtype=np.uint8)
    # print(image)


# 全局阈值
def threshold_demo(image):
    image = cv.imread(image)
    cv.namedWindow('title', 0)
    cv.resizeWindow("title", 640, 480)
    cv.imshow('title', image)
    img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    canny_img_one = cv.Canny(img, 300, 150)
    canny_img_two = canny_img_one.copy()
    for i in range(0, canny_img_one.shape[0]):
        for j in range(0, canny_img_one.shape[1]):
            canny_img_two[i, j] = 255 - canny_img_one[i, j]
    cv.imshow('edge', canny_img_two)
    cv.resizeWindow("edge", 1240, 480)
    cv.imwrite('test3.jpg', canny_img_two)
    cv.waitKey(0)


# 计算周长
def image_perimeter_caculate(x_space, y_space, image):
    img = cv.imread(image)
    # print(img)
    edge = cv.Canny(img, 200, 200)
    # 水平读取
    ans = []
    for y in range(0, edge.shape[0]):  # 高
        for x in range(0, edge.shape[1]):  # 宽
            if edge[y, x] != 0:
                ans = ans + [[x, y]]
    print(len(ans))
    # 表面积
    superficial = len(ans) * x_space * y_space
    # 周长
    perimeter = superficial / ((y_space + x_space) / 2)
    print(perimeter)


if __name__ == '__main__':
    # image = 'rectangle.png'
    # image = 'test.png'
    image = 'test3.jpg'
    # image = threshold_demo(image)
    # 输入参数（x像素间距，y像素间距），(图像全路径),()
    # build_image()
    X_SPACE = 1.17
    Y_SPACE = 2
    image_perimeter_caculate(X_SPACE, Y_SPACE, image)
