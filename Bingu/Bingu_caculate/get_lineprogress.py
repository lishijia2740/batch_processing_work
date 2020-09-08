import numpy as np
import cv2
from sklearn.linear_model import LinearRegression
import pandas as pd
from Bingu_caculate import caculate


class Get_Lineprogress():
    def __init__(self, image):
        self.__image = image
        img = cv2.imread(self.__image)
        self.__edge = cv2.Canny(img, 200, 200)

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image

    # 列（增长）方向读取
    def col_read_operation(self, ans=[]):
        """
        列（增长）方向读取
        :param ans:  [x,y,x1,y1,x2,y2...]
        :return:
        """
        edge = self.__edge
        for y in range(0, edge.shape[0]):  # 高
            for x in range(0, edge.shape[1]):  # 宽
                if edge[y, x] != 0:
                    ans = ans + [[x, y]]
                    self.__ans = ans

    # 行（增长）方向，提取边缘坐标
    def row_read_opertion(self, any=[]):
        """
        行（增长）方向，提取边缘坐标
        :param any: [x,y,x1,y1,x2,y2...]
        :return:
        """
        edge = self.__edge
        for y in range(0, edge.shape[1]):  # 宽
            for x in range(0, edge.shape[0]):  # 高
                if edge[x, y] != 0:
                    any = any + [[y, x]]
                    self.__any = any

    # 去重相同经度的坐标
    def deduplication_row(self):
        for i in range(len(self.__any) - 1):
            if self.__any[i + 1][0] == self.__any[i][0]:
                self.__any[i] = 0
        while True:
            self.__any.remove(0)
            if 0 not in self.__any:
                break
        self.__any = self.__any

    # 获取边缘线
    def get_marginal_line(self):
        x_scatter = []
        y_scatter = []
        for i in self.__any:
            x_scatter.append(i[0])
            y_scatter.append(-i[1])

        bottom_index = self.__any.index(self.__ans[-1])

        # 获取以bottom为界限的两列像素点
        marginal_lines_a = self.__any[:bottom_index]
        marginal_lines_b = self.__any[bottom_index:]
        return marginal_lines_a, marginal_lines_b

    # 构建像素坐标列表
    # a_new_list = get_lines(a_lines)
    # b_new_list = get_lines(b_lines)
    def get_pixel_lines(self, marginal_lines):
        """
        构建一个两列的数组
        :param marginal_lines:  [1,2,3,4,5,6,7,8,9...]
        :return:     [array([312,  50]), array([313,  47])....]
        """
        marginal_lines_list = []
        for i in marginal_lines:
            marginal_lines_list.append(i[0])
            marginal_lines_list.append(i[1])
        data1 = np.array(marginal_lines_list)
        array_row = data1.size // 2
        shape = data1.reshape(array_row, 2)
        new_list1 = list(shape)
        return new_list1

    def get_scatter(self):
        """
        取三个顶点
        :return: [1,2],[3,4],[5,6]
        """
        self.__left = self.__any[0]
        self.__bottom = self.__ans[-1]
        self.__right = self.__any[-1]
        return self.__left, self.__bottom, self.__right

    # test_alist = [left, bottom]
    # test_blist = [bottom, right]
    def get_test_list(self):
        """
        构建测试集
        :return: [[1,2],[1,2]],[[3,4],[3,4]]
        """
        return [self.__left, self.__bottom], [self.__bottom, self.__right]

    # 构建训练集
    # a_data_feature, a_data_target = build_data(a_new_list)
    # b_data_feature, b_data_target = build_data(b_new_list)

    # test_alist, p_a = build_data(test_alist)
    # test_blist, p_b = build_data(test_blist)
    def build_data(self, data_list):
        """
        将构建的训练样本分为，特征值和目标值
        :param data_list:  [1,2,3,4,5,6,7,8...]
        :return:    [[31]
                    [24]
                    [43]]
                    ,
                    [[5]
                    [6]
                    [7]]
        """
        name = ['x', 'y']
        data = pd.DataFrame(columns=name, data=data_list)
        data_feature = data.loc[:, 'x']
        data_target = data.loc[:, 'y']
        data_feature = np.array(data_feature).reshape(-1, 1)
        data_target = np.array(data_target).reshape(-1, 1)
        return data_feature, -data_target

    # 构建线性回归
    # regr = Line_Regression(a_data_feature, a_data_target)
    # regr1 = Line_Regression(b_data_feature, b_data_target)
    def line_regression(self, features, target):
        """

        :param features:    [[31]
                            [24]
                            [43]]
        :param target:      [[5]
                            [6]
                            [7]]
        :return:    model
        """
        regr = LinearRegression()
        regr.fit(features, target)
        return regr

    # 获取预测值
    def get_predict(self, regr, test_list):
        """

        :param regr:    model
        :param test_list:   [[31]
                            [24]
                            [43]]
        :return:            [[5]
                            [6]
                            [7]]
        """
        result = regr.predict(test_list)
        return result

    # 计算bottom
    # bottom_x, bottom_y = found_bottom(regr, regr1)
    # bottom = [bottom_x, bottom_y]
    def found_bottom(self, regr, regr1):
        """
        计算拟合交点的坐标
        :param regr:    model
        :param regr1:   model
        :return:    x,y
        """
        regr_coef_ = float(regr.coef_)  # 系数
        regr_intercept_ = float(regr.intercept_)  # 截距
        regr1_coef_ = float(regr1.coef_)
        regr1_intercept_ = float(regr1.intercept_)
        ff = regr_coef_ - regr1_coef_
        if regr_coef_ - regr1_coef_ < 0:
            ff = abs(regr_coef_ - regr1_coef_)
        x = round(abs(regr1_intercept_ - regr_intercept_) // ff)
        # x = np.array(x).reshape(-1, 1)
        y = round(float((regr_coef_ * x) + regr_intercept_))
        return x, y

    # 构建新顶点
    def new_scatter(self, result_a, result_b):
        """

        :param result_a:    [[5]
                            [6]
                            [7]]

        :param result_b:    [[5]
                            [6]
                            [7]]
        :return:    [1,2],[3,4]
        """
        left = [self.__left[0], int(result_a[0])]
        right = [self.__right[0], int(result_b[1])]
        return left, right


if __name__ == '__main__':
    # 图片处理
    getLineprogress = Get_Lineprogress('test5.jpg')
    getLineprogress.col_read_operation()
    getLineprogress.row_read_opertion()
    getLineprogress.deduplication_row()
    # 构建边缘直线
    a_lines, b_lines = getLineprogress.get_marginal_line()
    a_new_list = getLineprogress.get_pixel_lines(a_lines)
    b_new_list = getLineprogress.get_pixel_lines(b_lines)
    getLineprogress.get_scatter()
    test_alist, test_blist = getLineprogress.get_test_list()
    # 构建训练集，测试集
    a_data_feature, a_data_target = getLineprogress.build_data(a_new_list)
    b_data_feature, b_data_target = getLineprogress.build_data(b_new_list)
    test_alist, p_a = getLineprogress.build_data(test_alist)
    test_blist, p_b = getLineprogress.build_data(test_blist)

    # 构建模型，训练数据，预测结果
    regr = getLineprogress.line_regression(a_data_feature, a_data_target)
    regr1 = getLineprogress.line_regression(b_data_feature, b_data_target)
    result_a = getLineprogress.get_predict(regr, test_alist)
    result_b = getLineprogress.get_predict(regr1, test_blist)
    # 计算bottom
    bottom_x, bottom_y = getLineprogress.found_bottom(regr, regr1)
    bottom = [bottom_x, bottom_y]
    # 构建节点
    left, right = getLineprogress.new_scatter(result_a, result_b)
    # 三个顶点
    a_line = [left, bottom]
    b_line = [bottom, right]

    # 实例化计算类
    caculate = caculate.CaculateAngle()
    print('髌骨夹角角度为:', caculate.caculate_from_points(a_line, b_line))
