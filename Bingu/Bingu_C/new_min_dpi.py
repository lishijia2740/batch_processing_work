import cv2
import math


class New_Min_Dpi():
    def __init__(self, image):
        self.__image = image

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image

    def operation_image(self):
        self.__image = cv2.imread('test3.jpg', cv2.IMREAD_COLOR)

        edge = cv2.Canny(self.__image, 200, 200)

        ans = []
        for y in range(0, edge.shape[0]):  # 高
            for x in range(0, edge.shape[1]):  # 宽
                if edge[y, x] != 0:
                    ans = ans + [[y, x]]
        self.__ans = ans
        any = []
        for y in range(0, edge.shape[1]):  # 宽
            for x in range(0, edge.shape[0]):  # 高
                if edge[x, y] != 0:
                    any = any + [[x, y]]
        self.__any = any

    def identification_image_shape(self):
        pass
        # left = self.__ans[0]
        # bottom = self.__any[-1]
        # right = self.__ans[-1]
        # top = self.__any[0]
        # init_point = [right[0], bottom[1]]
        # print(left,right,bottom,top,in)
        # left_init_long = math.sqrt((init_point[0] - left[0]) ** 2 + (init_point[1] - left[1]) ** 2)
        # top_init_long = math.sqrt((init_point[0] - top[0]) ** 2 + (top[1] - init_point[1]) ** 2)
        # if left_init_long > top_init_long:
        #     self.__flag = 0
        # if top_init_long > left_init_long:
        #     self.__flag = 1
        # print(self.__flag)

    def write_newimage(self):
        # if self.__flag == 0:
        right = self.__any[-1]
        left = self.__any[0]
        avgnum = int((left[0] + right[0]) // 2)
        sub4 = self.__image[avgnum:, :]
        cv2.namedWindow("orient4", 0)  # 显示分割的子图2
        cv2.resizeWindow("orient4", 640, 480)
        cv2.imshow("orient4", sub4)
        cv2.imwrite('test5.jpg', sub4)
        cv2.waitKey(0)
        # if self.__flag == 1:
        #     top = self.__ans[-1]
        #     bottom = self.__ans[0]
        #     avgnum = int((top[1] + bottom[1]) // 2)
        #     sub4 = self.__image[:, avgnum:]
        #     cv2.namedWindow("orient4", 0)  # 显示分割的子图2
        #     cv2.resizeWindow("orient4", 640, 480)
        #     cv2.imshow("orient4", sub4)
        #     cv2.imwrite('test5.jpg', sub4)
        #     cv2.waitKey(0)


if __name__ == '__main__':
    new_min_dpi = New_Min_Dpi('test3.jpg')
    new_min_dpi.operation_image()
    # new_min_dpi.identification_image_shape()
    new_min_dpi.write_newimage()
