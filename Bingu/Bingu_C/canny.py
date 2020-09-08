import cv2 as cv


class Edge():
    def __init__(self, image):
        self.__image = image

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image

    def operation_image(self):
        image = cv.imread(self.__image)
        cv.namedWindow('title')
        # cv.imshow('title', image)
        img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        canny_img_one = cv.Canny(img, 300, 150)
        canny_img_two = canny_img_one.copy()
        for i in range(0, canny_img_one.shape[0]):
            for j in range(0, canny_img_one.shape[1]):
                canny_img_two[i, j] = 255 - canny_img_one[i, j]
        cv.imwrite('test3.jpg', canny_img_two)


if __name__ == '__main__':
    edge = Edge('test2.jpg')
    edge.operation_image()
