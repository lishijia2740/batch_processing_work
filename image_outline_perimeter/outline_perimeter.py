import cv2 as cv


class outline_perimeter:

    def __init__(self, image, x_space, y_space):
        self._image = image
        self._x_space = x_space
        self._y_space = y_space

    def processing_image(self):
        """
        处理图片，二值化
        :return:
        """
        image = cv.imread(self._image)
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

    def image_perimeter_caculate(self):
        """
        根据图片遍历像素点，计算周长
        :return:
        """
        image = self._image
        x_space = self._x_space
        y_space = self._y_space
        img = cv.imread(image)
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


def main(image, x_space, y_space):
    op = outline_perimeter(image, x_space, y_space)
    op.processing_image()
    op.image_perimeter_caculate()


if __name__ == '__main__':
    image = 'test3.jpg'
    # image = threshold_demo(image)
    # 输入参数（x像素间距，y像素间距），(图像全路径),()
    X_SPACE = 1.17
    Y_SPACE = 2
    # image_perimeter_caculate(X_SPACE, Y_SPACE, image)
    main(image, X_SPACE, Y_SPACE)
