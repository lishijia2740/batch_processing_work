from batch_command.batch_concat_to_csv import *
from batch_command.batch_concat_listdir import get_file_paths_by_regex
from smartimage.functions.label_operate import SmartLabel, _transform_physical_point_to_numpy_index
import SimpleITK as sitk
import pandas as pd
import numpy as np
import random
import shutil
import math
import json
import time
import csv
import re
import os


# 正则匹配单个文件
def matchfile(self, input_folder, pattern):
    file_names = os.listdir(input_folder)
    names = list(filter(lambda s: re.findall(pattern, s), file_names))
    if len(names) == 0:
        raise Exception('未找到匹配文件！')
    elif len(names) > 1:
        raise Exception('匹配文件数大于1！')
    elif len(names) == 1:
        path = os.path.join(input_folder, names[0])
        return path


# 计算夹角角度-2D
class CaculateAngle:

    def cross_point(self, line1, line2):  # 计算交点函数
        x1 = line1[0]  # 取四点坐标
        y1 = line1[1]
        x2 = line1[2]
        y2 = line1[3]

        x3 = line2[0]
        y3 = line2[1]
        x4 = line2[2]
        y4 = line2[3]

        if (x4 - x3) == 0:  # L2直线斜率不存在操作
            k2 = None
            b2 = 0
            x = x3
            k1 = (y2 - y1) * 1.0 / (x2 - x1)  # 计算k1,由于点均为整数，需要进行浮点数转化
            b1 = y1 * 1.0 - x1 * k1 * 1.0  # 整型转浮点型是关键
            y = k1 * x * 1.0 + b1 * 1.0
        elif (x2 - x1) == 0:
            k1 = None
            b1 = 0
            x = x1
            k2 = (y4 - y3) * 1.0 / (x4 - x3)
            b2 = y3 * 1.0 - x3 * k2 * 1.0
            y = k2 * x * 1.0 + b2 * 1.0
        else:
            k1 = (y2 - y1) * 1.0 / (x2 - x1)  # 计算k1,由于点均为整数，需要进行浮点数转化
            k2 = (y4 - y3) * 1.0 / (x4 - x3)  # 斜率存在操作
            b1 = y1 * 1.0 - x1 * k1 * 1.0  # 整型转浮点型是关键
            b2 = y3 * 1.0 - x3 * k2 * 1.0
            x = (b2 - b1) * 1.0 / (k1 - k2)
            y = k1 * x * 1.0 + b1 * 1.0
        return [x, y]

    # line1 = [0, 4, 0, 2]
    # line2 = [2, 0, 3, 0]
    # print(cross_point(line1, line2))

    # 三角形三条边长度求第二条边对角角度
    def caculate_from_triangle(self, line_a, line_b, line_c):
        """
        通过三角形三条边，利用三角函数计算cosB的值，再利用反余弦，求B的角度。
        :param line_a:  33
        :param line_b:  22
        :param line_c:  11

        :return:    float
        """
        line_a, line_b, line_c = line_a, line_b, line_c
        angle = (line_a ** 2 - line_b ** 2 + line_c ** 2) / (2 * line_a * line_c)
        return math.acos(angle) * 180 / math.pi

    # 三个点构成的夹角
    def caculate_from_points(self, point_A, point_B, point_C):
        """
        利用三个点，构建三角形
        :param point_A: [1,2]
        :param point_B: [1,2]，夹角，所求的角度的点
        :param point_C: [1,2]
        :return:    float
        """
        point_a = point_A
        point_b = point_B
        point_c = point_C
        # print(point_a, point_b, point_c)
        x1 = point_b[0] - point_a[0]
        y1 = point_a[1] - point_b[1]

        x2 = point_c[0] - point_a[0]
        y2 = point_a[1] - point_c[1]

        x3 = point_c[0] - point_b[0]
        y3 = point_c[1] - point_b[1]

        line_c = math.sqrt(x1 ** 2 + y1 ** 2)
        line_b = math.sqrt(x2 ** 2 + y2 ** 2)
        line_a = math.sqrt(x3 ** 2 + y3 ** 2)

        return self.caculate_from_triangle(line_a, line_b, line_c)

    # 两条直线的夹角
    def caculate_from_lines(self, line_regression_line_a, line_regression_line_b):
        """
        线性回归拟合出的两条直线
        :param line_regression_line_a:  [[713, -18], [611, -95]]
        :param line_regression_line_b: [[611, -95], [312, -2]]
        :return:    float
        """
        list1 = list(range(3))
        for i in line_regression_line_a:
            for j in line_regression_line_b:
                if i == j:
                    list1[1] = i
                    line_regression_line_a.remove(i)
                    line_regression_line_b.remove(j)
        list1[0] = random.choice(line_regression_line_a)
        list1[2] = random.choice(line_regression_line_b)
        point_A, point_B, point_C = list1[0], list1[1], list1[2]
        return self.caculate_from_points(point_A, point_B, point_C)


# 计算夹角角度-3D
class CaculateAngle_3D:

    # 三角形三条边长度求第二条边对角角度
    def caculate_from_triangle(self, line_a, line_b, line_c):
        """
        通过三角形三条边，利用三角函数计算cosB的值，再利用反余弦，求B的角度。
        :param line_a:  33
        :param line_b:  22
        :param line_c:  11

        :return:    float
        """
        line_a, line_b, line_c = line_a, line_b, line_c
        angle = (line_a ** 2 - line_b ** 2 + line_c ** 2) / (2 * line_a * line_c)
        return math.acos(angle) * 180 / math.pi

    # 三个点构成的夹角
    def caculate_from_points(self, point_a, point_b, point_c):
        """
        利用三个点，构建三角形
        :param point_A: [1,2]
        :param point_B: [1,2]，夹角，所求的角度的点
        :param point_C: [1,2]
        :return:    float
        """
        x1 = point_b[0] - point_a[0]
        y1 = point_a[1] - point_b[1]
        z1 = point_b[2] - point_a[2]

        x2 = point_c[0] - point_a[0]
        y2 = point_a[1] - point_c[1]
        z2 = point_a[2] - point_c[2]

        x3 = point_c[0] - point_b[0]
        y3 = point_c[1] - point_b[1]
        z3 = point_c[2] - point_b[2]

        line_c = math.sqrt(x1 ** 2 + y1 ** 2 + z1 ** 2)
        line_b = math.sqrt(x2 ** 2 + y2 ** 2 + z2 ** 2)
        line_a = math.sqrt(x3 ** 2 + y3 ** 2 + z3 ** 2)

        return self.caculate_from_triangle(line_a, line_b, line_c)

    # 两条直线的夹角
    def caculate_from_lines(self, line_regression_line_a, line_regression_line_b):
        """
        线性回归拟合出的两条直线
        :param line_regression_line_a:  [[713, -18], [611, -95]]
        :param line_regression_line_b: [[611, -95], [312, -2]]
        :return:    float
        """
        list1 = list(range(3))
        for i in line_regression_line_a:
            for j in line_regression_line_b:
                if i == j:
                    list1[1] = i
                    line_regression_line_a.remove(i)
                    line_regression_line_b.remove(j)
        list1[0] = random.choice(line_regression_line_a)
        list1[2] = random.choice(line_regression_line_b)
        point_A, point_B, point_C = list1[0], list1[1], list1[2]
        return self.caculate_from_points(point_A, point_B, point_C)


# # 髌骨计算类
# class KneeJson:
#
#     def _init(self, input_path, patella_itk_image, femur_itk_image):
#         self.caculateangle = CaculateAngle()
#         self.smartlabel = SmartLabel()
#         self.input_path = input_path
#         self.patella_itk_image = patella_itk_image
#         self.femur_itk_image = femur_itk_image
#         # self.patella_point = {}
#         # self.femur_point = {}
#         # self.point_o = None
#         # self.femur_number = 0
#         self.patella_point_dict = self.build_point(self.patella_itk_image)
#         self.femur_point_dict = self.build_point(self.femur_itk_image)
#
#     # def get_label_by_values(self, itk_image, value):
#     #     """
#     #     根据特定的数值生成新的image对象（二值标签）
#     #     :param itk_image:
#     #     :param value:
#     #     :return:
#     #     """
#     #     itk_image_arr = sitk.GetArrayFromImage(itk_image)
#     #     itk_image_arr[itk_image_arr != value] = 0
#     #     sitk_image = sitk.GetImageFromArray(itk_image_arr)
#     #     sitk_image.SetDirection(itk_image.GetDirection())
#     #     sitk_image.SetOrigin(itk_image.GetOrigin())
#     #     sitk_image.SetSpacing(itk_image.GetSpacing())
#     #     return sitk_image
#     def matchfile(self, input_folder, pattern):
#         file_names = os.listdir(input_folder)
#         names = list(filter(lambda s: re.findall(pattern, s), file_names))
#         if len(names) == 0:
#             raise Exception('未找到匹配文件！')
#         elif len(names) > 1:
#             raise Exception('匹配文件数大于1！')
#         elif len(names) == 1:
#             path = os.path.join(input_folder, names[0])
#             return path
#
#     def build_point(self, itk_image):
#         label_point = {}
#         itk_image_arr = sitk.GetArrayFromImage(itk_image)
#         itk_image_list = list(np.unique(itk_image_arr))
#         itk_image_list.remove(0)
#         for i in itk_image_list:
#             tmp_sitk = itk_image == i
#             label1 = self.smartlabel.from_sitk_image(tmp_sitk)
#             world_centroid_point = label1.centroid_point.to_list()
#             array_centroid_point = _transform_physical_point_to_numpy_index(tmp_sitk, world_centroid_point)  # (z, y, x)
#             label_point.update({i: [array_centroid_point[-1], array_centroid_point[-2]]})
#         return label_point
#
#     @staticmethod
#     def rotate(fixed_point, rotate_point, angle):
#         """
#         x' = (x - x0)*cosA - (y - y0)*sinA
#         y' = (y - y0)*cosA + (x -x0)*sinA
#         :param fixed_point: 参考点
#         :param rotate_point: 旋转点
#         :param angle: 夹角
#         :return:
#         """
#         x, y = rotate_point
#         x0, y0 = fixed_point
#         radians = math.radians(angle)
#         _x = (x - x0) * math.cos(radians) - (y - y0) * math.sin(radians)
#         _y = (y - y0) * math.cos(radians) + (x - x0) * math.sin(radians)
#         return [_x + x0, _y + y0]
#
#     def patella_angle_points(self):
#         """
#         得到三个点 中间的点为定点
#         Returns:
#             (x, y), (x, y), (x, y)
#         """
#         return self.patella_point_dict[4], self.patella_point_dict[3], self.patella_point_dict[2]
#
#     def patella_angle(self):
#         """
#         髌股关节面角：即髌骨内外关节面所成之角，正常约130°，大致与股沟角相当。
#         髌骨的夹角
#         :return:
#         """
#         # point_h = self.patella_point_dict[4]
#         # point_d = self.patella_point_dict[3]
#         # point_j = self.patella_point_dict[2]
#         patella_angle = self.caculateangle.caculate_from_points(*self.patella_angle_points())
#         # print('髌股关节面角：', patella_angle)
#         return patella_angle
#
#     def femur_angle_points(self):
#         """
#         得到三个点 中间的点为定点
#         Returns:
#             (x, y), (x, y), (x, y)
#         """
#         return self.patella_point_dict[10], self.patella_point_dict[8], self.patella_point_dict[6]
#
#     def femur_angle(self):
#         """
#         股沟角：由股骨内、外侧髁顶点至股骨滑车底连线所成的髁间角，正常为138°〜142°。在髌骨半脱位可增大，说明股骨下端发育不良可导致髌骨不稳定
#         股骨的夹角。
#         :return:
#         """
#         # point_c = self.patella_point_dict[10]
#         # point_a = self.patella_point_dict[8]
#         # point_b = self.patella_point_dict[6]
#
#         femur_angle = self.caculateangle.caculate_from_points(*self.femur_angle_points())
#         # self.femur_number = femur_angle
#         # print('股沟角的角度：', femur_angle)
#         return femur_angle
#
#     def fit_angle_points(self):
#         """
#         10 旋转 以 8为轴
#         旋转10,8,6角度的一半
#         Returns:
#             10’, 8 , 3
#             (x, y), (x, y), (x, y)
#         """
#         point10 = self.patella_point_dict[10]
#         point8 = self.femur_point_dict[8]
#         half_femur_angle = self.femur_angle() / 2
#         _point10 = self.rotate(point10, point8, half_femur_angle)
#         return _point10, point8, self.femur_point_dict[3]
#
#     def fit_angle(self):
#         """
#         适应角：在股沟角作平分线，其与髌骨最低点和沟底连线之间的夹角即适应角，正常此角偏向内髁侧，为-6°〜-9°，如偏向外髁侧，则为正值，适应角的大小提示髌骨的稳定情况。有髌骨不稳定者，其适应角均增大。
#         :return:
#         """
#
#         # fit_angle = abs(
#         # self.femur_angle() / 2 - self.caculateangle.caculate_from_points(self.patella_point_dict[3], self.femur_point_dict[8],
#         #                                self.femur_point_dict[6]))
#         # print('适应角的角度：', fit_angle)
#         # x = self.rotate(self.patella_point[3], self.double_center_angle()[0], fit_angle)
#         # return fit_angle, self.patella_point[3], self.femur_point[8], x
#         fit_angle = self.caculateangle.caculate_from_points(*self.fit_angle_points())
#         return fit_angle
#
#     def double_center_angle_points(self):
#         """
#         得到三个点 中间的点为定点
#         Returns:
#             (x, y), (x, y), (x, y)
#         """
#         point_o = [self.patella_point_dict[5][0] + (self.patella_point_dict[1][0] - self.patella_point_dict[5][0]) / 2,
#                    self.patella_point_dict[5][1] + (self.patella_point_dict[1][1] - self.patella_point_dict[5][1]) / 2]
#         return self.patella_point_dict[3], self.femur_point_dict[8], point_o
#
#     def double_center_angle(self):
#         """
#         双中心角：髌骨内外缘连线中点和沟底连线与股沟角平分线所成夹角称为双中心角，测量结果显示其与适应角数值近似
#         :return:
#         """
#         # point_o = [self.patella_point_dict[5][0] + (self.patella_point_dict[1][0] - self.patella_point_dict[5][0]) / 2,
#         #            self.patella_point_dict[5][1] + (self.patella_point_dict[1][1] - self.patella_point_dict[5][1]) / 2]
#         double_center_angle = self.caculateangle.caculate_from_points(*self.double_center_angle_points())
#         # print('双中心角度数：', double_center_angle)
#         # self.point_o = point_o
#         return double_center_angle
#
#     def outside_patella_angle_points(self):
#         """
#         得到三个点 中间的点为定点
#         Returns:
#             (x, y), (x, y), (x, y)
#         """
#         cross_point = self.caculateangle.cross_point(self.patella_point_dict[4] + self.patella_point_dict[3],
#                                                      self.femur_point_dict[10] + self.femur_point_dict[6])
#         return self.femur_point_dict[10], cross_point, self.femur_point_dict[4]
#
#     def outside_patella_angle(self):
#         """
#         外侧髌股角：为股骨内、外侧髁连线与髌骨外侧关节面所成之角，正常约为15°。在髌骨半脱位，两线多呈平行，甚至向内成角
#         :return:
#         """
#
#         # outside_patella_angle = self.caculateangle.caculate_from_points(self.femur_point_dict[10], cross_point,
#         #                                                                 self.patella_point_dict[4])
#         outside_patella_angle = self.caculateangle.caculate_from_points(*self.outside_patella_angle_points())
#         # print('外侧髌股角度：', outside_patella_angle)
#         return outside_patella_angle
#
#     def patella_slant_angle_points(self):
#         """
#         得到三个点 中间的点为定点
#         Returns:
#             (x, y), (x, y), (x, y)
#         """
#         cross_point = self.caculateangle.cross_point(self.patella_point_dict[5] + self.patella_point_dict[1],
#                                                      self.femur_point_dict[10] + self.femur_point_dict[6])
#         return self.femur_point_dict[6], cross_point, self.patella_point_dict[1]
#
#     def patella_slant_angle(self):
#         """
#         髌倾斜角：为髌骨内外缘连线及股骨内、外侧髁连线相交之角，正常约为11°，在髌骨半脱位时可增大。
#         :return:
#         """
#         # cross_point = self.caculateangle.cross_point(self.patella_point_dict[5] + self.patella_point_dict[1],
#         #                                              self.femur_point_dict[10] + self.femur_point_dict[6])
#         # patella_slant_angle = self.caculateangle.caculate_from_points(self.femur_point_dict[6], cross_point,
#         #                                                               self.patella_point_dict[1])
#         patella_slant_angle = self.caculateangle.caculate_from_points(*self.patella_slant_angle_points())
#         # print('髌倾斜角度数：', patella_slant_angle)
#         return patella_slant_angle
#
#     def lateral_joint_space_points(self):
#         """
#         得到两个点 用于计算外侧髌骨间隙
#         Returns:
#             (x, y), (x, y)
#         """
#         return self.femur_point_dict[9], self.patella_point_dict[4]
#
#     def lateral_joint_space(self):
#         """
#         外侧髌骨间隙
#         :return:
#         """
#         point_9, point_4 = self.lateral_joint_space_points()
#         line_GH = math.sqrt((point_9[0] - point_4[0]) ** 2 + (point_9[1] - point_4[1]) ** 2)
#         image_space = self.patella_itk_image.GetSpacing()
#         image_space_x = image_space[0]
#         image_space_y = image_space[1]
#         space = (image_space_x + image_space_y) / 2
#         return line_GH * space
#
#     def medial_joint_space_points(self):
#         """
#         得到两个点 用于计算内侧髌骨间隙
#         Returns:
#             (x, y), (x, y)
#         """
#         return self.femur_point_dict[7], self.patella_point_dict[2]
#
#     def medial_joint_space(self):
#         """
#         内侧髌骨间隙
#         :return:
#         """
#         point_7, point2 = self.medial_joint_space_points()
#         line_IJ = math.sqrt((point_7[0] - point2[0]) ** 2 + (point_7[1] - point2[1]) ** 2)
#         image_space = self.patella_itk_image.GetSpacing()
#         image_space_x = image_space[0]
#         image_space_y = image_space[1]
#         space = (image_space_x + image_space_y) / 2
#         return line_IJ * space
#
#     def patella_index_points(self):
#         """
#         得到4个点
#         Returns:
#             ((x, y), (x, y)), ((x, y), (x, y))
#         Returns:
#
#         """
#         return self.lateral_joint_space_points(), self.medial_joint_space_points()
#
#     def patella_index(self):
#         """
#         髌股指数：内侧髌股关节间隙最短距离与外侧髌股关节最短距离之比。正常髌骨指数＜1.6，髌股关节炎因外侧超负荷，致软骨磨损变薄，髌股指数增大>1.6，可表明髌骨倾斜或半脱位
#         :return:
#         """
#         line_GH = self.lateral_joint_space()
#         line_IJ = self.medial_joint_space()
#         # print('髌股指数：', line_IJ / line_GH)
#         return line_IJ / line_GH
#
#     def patellafacetratio(self):
#         """
#         髌骨关节面比例
#         :return:
#         """
#         return None
#
#     def return_caculate_result(self):
#         """
#         返回计算结果
#         :return:
#         """
#         femur_angle = self.femur_angle()
#         patella_angle = self.patella_angle()
#         fit_angle = self.fit_angle()
#         double_center_angle = self.double_center_angle()
#         outside_patella_angle = self.outside_patella_angle()
#         patella_slant_angle = self.patella_slant_angle()
#         medial_joint_space = self.medial_joint_space()
#         lateral_joint_space = self.lateral_joint_space()
#         patella_index = self.patella_index()
#         AccNum_SeqNum_list = self.input_path.split('/')[-1]
#         tmp_list = AccNum_SeqNum_list.split('__')
#         AccNum_SeqNum = tmp_list[-3] + '__' + tmp_list[-2] + '__' + tmp_list[-1]
#         # res_dict = {'AccNum': AccNum_SeqNum_list, 'AccNum_SeqNum': AccNum_SeqNum, '股沟角的角度': femur_angle,
#         #             '髌股关节面角': patella_angle, '适应角的角度': fit_angle, '双中心角度数': double_center_angle,
#         #             '外侧髌股角度': outside_patella_angle, '髌倾斜角度数': patella_slant_angle,
#         #             '内侧关节间隙': medial_joint_space, '外侧关节间隙': lateral_joint_space, '髌股指数': patella_index}
#         res_dict = {'AccNum': AccNum_SeqNum_list, 'AccNum_SeqNum': AccNum_SeqNum, 'SulcusAngle': femur_angle,
#                     'PatellaFacetAngle': patella_angle, 'CongruenceAngle': fit_angle,
#                     'DoubleCentralAngle': double_center_angle,
#                     'PeripheralPatellaFemurAngle': outside_patella_angle, 'PatellaTiltingAngle': patella_slant_angle,
#                     'MedialJointSpace': medial_joint_space, 'LaterialJointSpace': lateral_joint_space,
#                     'PateloFemoralIndex': patella_index}
#         return res_dict
# 髌骨计算类
class KneeJson:

    def _init(self, input_path, **kwargs):
        self.caculateangle = CaculateAngle()
        self.smartlabel = SmartLabel()
        self.input_path = input_path
        self.label_path_list = []
        self.point_dict = {}
        self.build_label()
        self.build_point()

    def matchfile(self, input_folder, patterns):
        names = []
        file_names = os.listdir(input_folder)
        patterns = patterns.split(',')
        for pattern in patterns:
            file = list(filter(lambda s: re.findall(pattern, s), file_names))
            if file:
                names.append(file[0])
        if len(names) == 0:
            return 0
        elif len(names) > 1:
            raise Exception('匹配文件数大于1！')
        elif len(names) == 1:
            path = os.path.join(input_folder, names[0])
            return path

    def build_label(self):
        pattern_list = ['^label__49207_.*.nii.gz,^label__49206_.*.nii.gz',
                        '^label__2749-5824_.*.nii.gz,^label__2749-5825_.*.nii.gz',
                        '^label__49156_.*.nii.gz,^label__49155_.*.nii.gz',
                        '^label__2748-5824_.*.nii.gz,^label__2748-5825_.*.nii.gz',
                        '^label__49210_.*.nii.gz,^label__49209_.*.nii.gz',
                        '^label__39858_.*.nii.gz,^label__39859_.*.nii.gz',
                        '^label__49311_.*.nii.gz,^label__49310_.*.nii.gz',
                        '^label__49317_.*.nii.gz,^label__49316_.*.nii.gz',
                        '^label__49314_.*.nii.gz,^label__49313_.*.nii.gz',
                        '^label__39860_.*.nii.gz,^label__39859_.*.nii.gz']
        label_list = []
        for patterns in pattern_list:
            label_path = self.matchfile(self.input_path, patterns)
            label_list.append(label_path)
        self.label_path_list = label_list

    def build_point(self):
        point_dict = {}
        for index in range(len(self.label_path_list)):
            if not self.label_path_list[index]:
                point_dict.update({index + 1: 0})
            else:
                itk_image_arr = sitk.ReadImage(self.label_path_list[index])
                tmp = np.unique(sitk.GetArrayFromImage(itk_image_arr))
                if len(tmp) == 1:
                    point_dict.update({index + 1: 0})
                else:
                    label1 = self.smartlabel.from_sitk_image(itk_image_arr)
                    world_centroid_point = label1.centroid_point.to_list()
                    array_centroid_point = _transform_physical_point_to_numpy_index(itk_image_arr,
                                                                                    world_centroid_point)  # (z, y, x)
                    point_dict.update({index + 1: [array_centroid_point[-1], array_centroid_point[-2]]})
        self.point_dict = point_dict

    @staticmethod
    def rotate(fixed_point, rotate_point, angle):
        """
        x' = (x - x0)*cosA - (y - y0)*sinA
        y' = (y - y0)*cosA + (x -x0)*sinA
        :param fixed_point: 参考点
        :param rotate_point: 旋转点
        :param angle: 夹角
        :return:
        """
        x, y = rotate_point
        x0, y0 = fixed_point
        radians = math.radians(angle)
        _x = (x - x0) * math.cos(radians) - (y - y0) * math.sin(radians)
        _y = (y - y0) * math.cos(radians) + (x - x0) * math.sin(radians)
        return [_x + x0, _y + y0]

    def patella_angle_points(self):
        """
        得到三个点 中间的点为定点
        Returns:
            (x, y), (x, y), (x, y)
        """
        tmp_point_list = [self.point_dict[4], self.point_dict[3], self.point_dict[2]]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[1], tmp_point_list[2]

    def patella_angle(self):
        """
        髌股关节面角：即髌骨内外关节面所成之角，正常约130°，大致与股沟角相当。
        髌骨的夹角
        :return:
        """
        tmp_point_list = [*self.patella_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        patella_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
        return patella_angle

    def femur_angle_points(self):
        """
        得到三个点 中间的点为定点
        Returns:
            (x, y), (x, y), (x, y)
        """
        tmp_point_list = [self.point_dict[10], self.point_dict[8], self.point_dict[6]]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[1], tmp_point_list[2]

    def femur_angle(self):
        """
        股沟角：由股骨内、外侧髁顶点至股骨滑车底连线所成的髁间角，正常为138°〜142°。在髌骨半脱位可增大，说明股骨下端发育不良可导致髌骨不稳定
        股骨的夹角。
        :return:
        """
        tmp_point_list = [*self.femur_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        else:
            patella_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
            return patella_angle

    def fit_angle_points(self):
        """
        10 旋转 以 8为轴
        旋转10,8,6角度的一半
        Returns:
            10’, 8 , 3
            (x, y), (x, y), (x, y)
        """
        _point10 = ''
        tmp_point_list = [self.point_dict[10], self.point_dict[8], self.point_dict[3]]
        if self.femur_angle() != 'NA':
            half_femur_angle = self.femur_angle() / 2
            for i in range(len(tmp_point_list)):
                if not tmp_point_list[i]:
                    tmp_point_list[i] = 'NA'
                    _point10 = 'NA'
            if 'NA' not in tmp_point_list[:2]:
                _point10 = self.rotate(self.point_dict[10], self.point_dict[8], half_femur_angle)
        else:
            _point10 = 'NA'
        return _point10, tmp_point_list[1], tmp_point_list[-1]

    def fit_angle(self):
        """
        适应角：在股沟角作平分线，其与髌骨最低点和沟底连线之间的夹角即适应角，正常此角偏向内髁侧，为-6°〜-9°，如偏向外髁侧，则为正值，适应角的大小提示髌骨的稳定情况。有髌骨不稳定者，其适应角均增大。
        :return:
        """
        tmp_point_list = [*self.fit_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        fit_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
        return fit_angle

    def double_center_angle_points(self):
        """
        得到三个点 中间的点为定点
        Returns:
            (x, y), (x, y), (x, y)
        """
        # point_o = [self.point_dict[5][0] + (self.point_dict[1][0] - self.point_dict[5][0]) / 2,
        #            self.point_dict[5][1] + (self.point_dict[1][1] - self.point_dict[5][1]) / 2]
        # return self.patella_point_dict[3], self.femur_point_dict[8], point_o
        if self.point_dict[5] and self.point_dict[1]:
            point_o = [self.point_dict[5][0] + (self.point_dict[1][0] - self.point_dict[5][0]) / 2,
                       self.point_dict[5][1] + (self.point_dict[1][1] - self.point_dict[5][1]) / 2]
        else:
            point_o = []
        tmp_point_list = [self.point_dict[3], self.point_dict[8], point_o]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[1], tmp_point_list[2]

    def double_center_angle(self):
        """
        双中心角：髌骨内外缘连线中点和沟底连线与股沟角平分线所成夹角称为双中心角，测量结果显示其与适应角数值近似
        :return:
        """
        tmp_point_list = [*self.double_center_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        double_center_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
        return double_center_angle

    def outside_patella_angle_points(self):
        """
        得到三个点 中间的点为定点
        Returns:
            (x, y), (x, y), (x, y)
        """
        if self.point_dict[4] and self.point_dict[3] and self.point_dict[10] and self.point_dict[6]:
            cross_point = self.caculateangle.cross_point(self.point_dict[4] + self.point_dict[3],
                                                         self.point_dict[10] + self.point_dict[6])
        else:
            cross_point = 'NA'
        tmp_point_list = [self.point_dict[10], self.point_dict[4]]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], cross_point, tmp_point_list[1]
        # return self.point_dict[10], cross_point, self.point_dict[4]

    def outside_patella_angle(self):
        """
        外侧髌股角：为股骨内、外侧髁连线与髌骨外侧关节面所成之角，正常约为15°。在髌骨半脱位，两线多呈平行，甚至向内成角
        :return:
        """
        tmp_point_list = [*self.outside_patella_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        outside_patella_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
        return outside_patella_angle

    def patella_slant_angle_points(self):
        """
        得到三个点 中间的点为定点
        Returns:
            (x, y), (x, y), (x, y)
        """
        if self.point_dict[5] and self.point_dict[1] and self.point_dict[10] and self.point_dict[6]:
            cross_point = self.caculateangle.cross_point(self.point_dict[5] + self.point_dict[1],
                                                         self.point_dict[10] + self.point_dict[6])
        else:
            cross_point = []
        tmp_point_list = [self.point_dict[6], self.point_dict[1], cross_point]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[-1], tmp_point_list[1]
        # return self.femur_point_dict[6], cross_point, self.patella_point_dict[1]

    def patella_slant_angle(self):
        """
        髌倾斜角：为髌骨内外缘连线及股骨内、外侧髁连线相交之角，正常约为11°，在髌骨半脱位时可增大。
        :return:
        """
        # cross_point = self.caculateangle.cross_point(self.patella_point_dict[5] + self.patella_point_dict[1],
        #                                              self.femur_point_dict[10] + self.femur_point_dict[6])
        # patella_slant_angle = self.caculateangle.caculate_from_points(self.femur_point_dict[6], cross_point,
        #                                                               self.patella_point_dict[1])
        tmp_point_list = [*self.patella_slant_angle_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        patella_slant_angle = self.caculateangle.caculate_from_points(*tmp_point_list)
        return patella_slant_angle

    def lateral_joint_space_points(self):
        """
        得到两个点 用于计算外侧髌骨间隙
        Returns:
            (x, y), (x, y)
        """
        tmp_point_list = [self.point_dict[9], self.point_dict[4]]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[1]
        # return self.femur_point_dict[9], self.patella_point_dict[4]

    def lateral_joint_space(self):
        """
        外侧髌骨间隙
        :return:
        """
        tmp_point_list = [*self.lateral_joint_space_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        point_9, point_4 = tmp_point_list
        line_GH = math.sqrt((point_9[0] - point_4[0]) ** 2 + (point_9[1] - point_4[1]) ** 2)
        for i in self.label_path_list:
            if i:
                image_space = sitk.ReadImage(i).GetSpacing()
                image_space_x = image_space[0]
                image_space_y = image_space[1]
                space = (image_space_x + image_space_y) / 2
                return line_GH * space

    def medial_joint_space_points(self):
        """
        得到两个点 用于计算内侧髌骨间隙
        Returns:
            (x, y), (x, y)
        """
        # return self.femur_point_dict[7], self.patella_point_dict[2]
        tmp_point_list = [self.point_dict[7], self.point_dict[2]]
        for i in range(len(tmp_point_list)):
            if not tmp_point_list[i]:
                tmp_point_list[i] = 'NA'
        return tmp_point_list[0], tmp_point_list[1]

    def medial_joint_space(self):
        """
        内侧髌骨间隙
        :return:
        """
        tmp_point_list = [*self.medial_joint_space_points()]
        if 'NA' in tmp_point_list:
            return 'NA'
        point_7, point_2 = tmp_point_list
        line_GH = math.sqrt((point_7[0] - point_2[0]) ** 2 + (point_7[1] - point_2[1]) ** 2)
        for i in self.label_path_list:
            if i:
                image_space = sitk.ReadImage(i).GetSpacing()
                image_space_x = image_space[0]
                image_space_y = image_space[1]
                space = (image_space_x + image_space_y) / 2
                return line_GH * space

    def patella_index_points(self):
        """
        得到4个点
        Returns:
            ((x, y), (x, y)), ((x, y), (x, y))
        Returns:

        """
        return self.lateral_joint_space_points(), self.medial_joint_space_points()

    def patella_index(self):
        """
        髌股指数：内侧髌股关节间隙最短距离与外侧髌股关节最短距离之比。正常髌骨指数＜1.6，髌股关节炎因外侧超负荷，致软骨磨损变薄，髌股指数增大>1.6，可表明髌骨倾斜或半脱位
        :return:
        """
        line_GH = self.lateral_joint_space()
        line_IJ = self.medial_joint_space()
        if 'NA' in [line_GH, line_IJ]:
            return 'NA'
        # print('髌股指数：', line_IJ / line_GH)
        return line_IJ / line_GH

    def patellafacetratio(self):
        """
        髌骨关节面比例
        :return:
        """
        return None

    def return_caculate_result(self):
        """
        返回计算结果
        :return:
        """
        femur_angle = self.femur_angle()
        patella_angle = self.patella_angle()
        fit_angle = self.fit_angle()
        double_center_angle = self.double_center_angle()
        outside_patella_angle = self.outside_patella_angle()
        patella_slant_angle = self.patella_slant_angle()
        medial_joint_space = self.medial_joint_space()
        lateral_joint_space = self.lateral_joint_space()
        patella_index = self.patella_index()
        AccNum_SeqNum_list = self.input_path.split('/')[-1]
        tmp_list = AccNum_SeqNum_list.split('__')
        AccNum_SeqNum = tmp_list[-3] + '__' + tmp_list[-2] + '__' + tmp_list[-1]
        res_dict = {'AccNum': AccNum_SeqNum_list, 'AccNum_SeqNum': AccNum_SeqNum, 'SulcusAngle': femur_angle,
                    'PatellaFacetAngle': patella_angle, 'CongruenceAngle': fit_angle,
                    'DoubleCentralAngle': double_center_angle,
                    'PeripheralPatellaFemurAngle': outside_patella_angle, 'PatellaTiltingAngle': patella_slant_angle,
                    'MedialJointSpace': medial_joint_space, 'LaterialJointSpace': lateral_joint_space,
                    'PateloFemoralIndex': patella_index}
        return res_dict


# 框架外统计(配置文件）
class OutsideCreatMeasurement:
    def remove_space(self, list1):
        list2 = []
        for i in list1:
            i = i.strip()
            list2.append(i)
        return list2

    def concat_alldata_csv(self, input_path, output_path):
        if os.path.exists(output_path):
            print('文件已存在！')
        else:
            filenames = os.listdir(input_path)
            pdf = pd.DataFrame()
            for file in filenames:
                file_path = os.path.join(input_path, file)
                filedata = pd.read_csv(file_path)
                pdf = pd.concat([pdf, filedata], axis=0, ignore_index=True, sort=False)
            try:
                pdf = pdf.sort_values('DataSet')
            except:
                pass
            pdf = pdf.iloc[:, 1:]
            pdf.index += 1
            pdf.to_csv(output_path, na_rep='NA')
            print('请查看clinical_csv目录，目标文件已生成！')

    def concat_partdata_csv(self, folders_path, output_dir, images_re, labels_re, plabels_re):
        """
        输入（test，train，validate）上层文件夹路径，返回每个image的csv格式文件
        :param folder_path: （test，train，validate）上层文件夹路径
        :param output_dir:  输出文件全路径
        :param images_re:   匹配image正则表达式
        :param labels_re:   匹配label正则表达式
        :param plabels_re:  匹配plabel正则表达式
        :return:    csv格式文件
        """
        num_list = []
        file_path = get_file_paths_by_regex(folders_path, images_re, labels_re, plabels_re)
        file_path_list = file_path
        for i in file_path_list:
            for j in range(len(i['image_paths'])):
                num_list.append(j)
            break
        for n in num_list:
            pdf = pd.DataFrame()
            df = pd.DataFrame()
            output_path = ''
            for i in file_path_list:
                if i['image_paths'][n] == '':
                    continue
                else:
                    res = get_excel_json_run(i['image_paths'][n], i['label_paths'], i['plabel_paths'])
                    data = pd.DataFrame(res)
                    tmp = data.iloc[:, 0]
                    data = data.T.rename(columns=tmp.T)
                    data = data.iloc[1:, :]
                    p = (i['image_paths'][n]).split('/')
                    data.insert(1, 'DataSet', p[-3])
                    data.insert(2, 'ImageName', p[-1])
                    df = pd.concat([df, data], axis=0, ignore_index=True)
                    output_path = os.path.join(output_dir, '{}.csv'.format(p[-1][:-7]))
            if output_path:
                pass
            else:
                output_path = os.path.join(output_dir, 'image.csv')
            pdf = pd.concat([pdf, df], axis=0, ignore_index=True)
            pdf.index += 1
            pdf.to_csv(output_path, na_rep='NA')
            print('请等待，部分目标文件已生成！')

    def run(self, input_path, output_dir, image_patterns, label_patterns, plabel_patterns,
            continue_process_flag=False, **kwargs):
        """
        根据配置文件拼接正则表达式+启动程序
        :param input_path:
        :return: str ,'/data/medical-ai2/Seg3D/test/paper_excel/statistics.csv'
        """
        if not output_dir:
            output_dir = os.path.join(input_path, 'clinical_csv',
                                      'paper_csv_%s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                      'csv')
            os.makedirs(output_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'Measurements.csv')
        images_re = image_patterns.split(',')
        labels_re = label_patterns.split(',')
        plabels_re = plabel_patterns.split(',')
        image_patterns = self.remove_space(images_re)
        label_patterns = self.remove_space(labels_re)
        plabel_patterns = self.remove_space(plabels_re)
        self.concat_partdata_csv(input_path, output_dir, image_patterns, label_patterns, plabel_patterns)
        self.concat_alldata_csv(output_dir, output_path)
        if continue_process_flag:
            try:
                config_dict = read_config_return_dict(kwargs.get('batch_csv_process_path'))
                measurements_deep_process(output_path, config_dict)
                measurements_different_value(output_path, config_dict)
                print('Measurement.csv后续处理完成！')
            except:
                print('没有batch_csv_config后续处理配置文件！')
        else:
            print('不进行Measurement.csv后续处理。')


# 旧 CT MR图像时间，类型排序
class SortImageName:
    def __init__(self):
        self.input_path = None
        self.output_path = None

    def get_all_file_Anumber(self):
        res_list = []
        all_dirname_list = os.listdir(self.input_path)
        for dirname in all_dirname_list:
            if os.path.isdir(os.path.join(self.output_path, dirname)):
                res_list.append(dirname.split('__')[0])
        return list(set(res_list))

    def get_same_Anumber_imagefile(self, Anumber):
        res_list = []
        all_file_list = os.listdir(self.output_path)
        for file in all_file_list:
            if file.startswith(Anumber):
                res_list.append(file)
        return res_list

    def image_time_sort(self, input_list):
        image_time_list = []
        image_tag_list = []
        for dir in input_list:
            file_name_list = dir.split('__')[1:]
            file_name = '__'.join(file_name_list)
            image_time_json = file_name + '.json'
            image_time_json_path = os.path.join(self.output_path, dir, image_time_json)
            with open(image_time_json_path, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
            image_time = json_data[0]['0008|0032']
            image_tag = json_data[0]['0020|1041']
            image_time_list.append(image_time)
            image_tag_list.append(image_tag)
        np_argsort_index = list(np.argsort(image_time_list))
        sort_index_list = sorted(image_time_list)
        tmp_list = []
        for i in image_time_list:
            if image_time_list.count(i) > 1:
                tmp_list.append(i)
        list1 = []
        for j in set(tmp_list):
            for n in range(len(sort_index_list)):
                if sort_index_list[n] == j:
                    list1.append(n)
            list2 = []
            for z in list1:
                list2.append(image_tag_list[np_argsort_index[z]])
            np_sort_index_list2 = list(np.argsort(list2))
            for res_index in list1:
                sort_index_list[res_index] = np_sort_index_list2[0]
                np_sort_index_list2.pop(0)
        res = []
        for r in np_argsort_index:
            res.append(input_list[r])
        return res

    def matchfile(self, input_folder, pattern):
        file_names = os.listdir(input_folder)
        names = list(filter(lambda s: re.findall(pattern, s), file_names))
        if len(names) == 0:
            raise Exception('未找到匹配文件！')
        elif len(names) > 1:
            raise Exception('匹配文件数大于1！')
        elif len(names) == 1:
            path = os.path.join(input_folder, names[0])
            return path

    def _matchfile(self, input_folder, pattern):
        # file_names = os.listdir(input_folder)
        # names = list(filter(lambda s: re.findall(pattern, s), file_names))
        # return names
        names = []
        index = []
        dir_names = sorted(os.listdir(input_folder))
        for dir in range(len(dir_names)):
            dir_path = os.path.join(input_folder, dir_names[dir])
            file_names = os.listdir(dir_path)
            name = list(filter(lambda s: re.findall(pattern, s), file_names))
            for i in range(len(name)):
                name[i] = os.path.join(dir_path, name[i])
                index.append(dir)
            names += name
        return names, index

    def get_same_Anumber_image_type(self, input_list, json_name):
        res = []
        for dir in input_list:
            dir_path = os.path.join(self.output_path, dir)
            file_json = self.matchfile(dir_path, json_name)
            with open(file_json, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
            type_number = json_data['class_array'].index(1)
            image_type = json_data['class_names'][type_number]
            res.append(image_type)
        return res

    def image_type_sort(self, time_sort_image_list, input_list, reference_head, reference_foot, no_reference):
        index_list = reference_head + reference_foot
        correct_list = []
        error_list = []
        res_correct_list = []
        for i in index_list:
            for index in range(len(input_list)):
                image_type = input_list[index]
                if i in image_type:
                    res_correct_list.append(index)
        no_ref_list = [y for y in range(len(input_list)) if y not in res_correct_list]
        tmp_no_list = []
        for n in no_ref_list:
            for no in no_reference:
                if no in input_list[n]:
                    tmp_no_list.append(n)
        # res_correct_list = list(set(res_correct_list))
        # print(res_correct_list)
        if not tmp_no_list:
            if res_correct_list == sorted(res_correct_list):
                correct_list = time_sort_image_list
            else:
                error_list = time_sort_image_list
        elif tmp_no_list == no_ref_list:
            if res_correct_list == sorted(res_correct_list):
                correct_list = time_sort_image_list
        else:
            error_list = time_sort_image_list
        return correct_list, error_list

    def update_image_type(self, input_list, json_name):
        for dir in input_list:
            dir_path = os.path.join(self.output_path, 'correct', dir)
            json_file = self.matchfile(dir_path, json_name)
            with open(json_file, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
            type_number = json_data['class_array'].index(1)
            image_type = json_data['class_names'][type_number]
            update_dir_name_list = dir.split('__')
            if update_dir_name_list[2] == 'nan':
                update_dir_name_list[2] = image_type
            else:
                update_dir_name_list[2] = update_dir_name_list[2] + '-' + image_type
            update_dir_name = '__'.join(update_dir_name_list)
            tmp_name_list = update_dir_name_list
            update_file_name_list = tmp_name_list[1:]
            update_file_name = '__'.join(update_file_name_list)
            # json_data['class_names'][type_number] = update_dir_name_list[2]
            folder_path = json_data['folder_path'].split('/')
            folder_path[-1] = update_dir_name
            json_data['folder_path'] = '/'.join(folder_path)
            before_dir_name_list = dir.split('__')[1:]
            before_file_name = '__'.join(before_dir_name_list)
            with open(json_file, 'w', encoding='utf8')as f:
                json.dump(json_data, f, indent=4)
            os.rename(os.path.join(dir_path, before_file_name + '.json'),
                      os.path.join(dir_path, update_file_name + '.json'))
            os.rename(os.path.join(dir_path, before_file_name + '.nii.gz'),
                      os.path.join(dir_path, update_file_name + '.nii.gz'))
            os.rename(dir_path, os.path.join(self.output_path, 'correct', update_dir_name))

    def update_sorted_image_type(self, no_reference, json_name):
        input_path = os.path.join(self.output_path, 'correct')
        dir_list = os.listdir(input_path)
        count = 1
        image_type = ''
        for type in no_reference:
            for dir in dir_list:
                dir_path = os.path.join(input_path, dir)
                dir_name_list = dir.split('__')
                if type in dir:
                    if count == 1:
                        count += 1
                        image_type = type
                    else:
                        if image_type[-1].isdigit():
                            image_type = str(dir_name_list[2])[:-1] + str(int(image_type[-1]) + 1)
                        dir_name_list[2] = image_type
                        dir_new = '__'.join(dir_name_list)
                        json_file = self.matchfile(os.path.join(input_path, dir), json_name)
                        with open(json_file, 'r', encoding='utf8') as fp:
                            json_data = json.load(fp)
                        update_file_name_list = dir_name_list[1:]
                        update_file_name = '__'.join(update_file_name_list)
                        before_dir_name_list = dir.split('__')[1:]
                        before_file_name = '__'.join(before_dir_name_list)
                        folder_path = json_data['folder_path'].split('/')
                        folder_path[-1] = '__'.join(dir_name_list[1:])
                        json_data['folder_path'] = '/'.join(folder_path)
                        type_names = json_data['class_names']
                        # image_type = update_file_name
                        # type_number = json_data['class_array'].index(1)
                        for type_name in type_names:
                            if image_type in type_name:
                                type_name_index = type_names.index(type_name)
                                type_number = list(np.zeros_like(json_data['class_array']))
                                type_number[type_name_index] = 1
                                json_data['class_array'] = type_number
                        with open(json_file, 'w', encoding='utf8')as f:
                            json.dump(json_data, f, indent=4)
                        os.rename(os.path.join(dir_path, before_file_name + '.json'),
                                  os.path.join(dir_path, update_file_name + '.json'))
                        os.rename(os.path.join(dir_path, before_file_name + '.nii.gz'),
                                  os.path.join(dir_path, update_file_name + '.nii.gz'))
                        os.rename(os.path.join(input_path, dir), os.path.join(input_path, dir_new))
                        count += 1

    def link_save(self, output_path):
        input_path_dir = os.listdir(self.input_path)
        if not output_path:
            output_path = os.path.join(self.input_path, 'tmp_sort_dir')
        self.output_path = output_path
        for dir in input_path_dir:
            if dir == 'tmp_sort_dir':
                continue
            dir_path = os.path.join(self.input_path, dir)
            if os.path.isdir(dir_path):
                output = os.path.join(output_path, dir)
                os.makedirs(output, exist_ok=True)
                file_list = os.listdir(dir_path)
                for file in file_list:
                    file_path = os.path.join(dir_path, file)
                    if os.path.isfile(file_path):
                        os.link(file_path, os.path.join(output, file))

    def link_saves(self, output_path):
        # 图像类型文件夹
        input_path_dir = os.listdir(self.input_path)
        if not output_path:
            output_path = os.path.join(self.input_path, 'tmp_sort_dir')
        self.output_path = output_path
        # dir：图像类型文件名
        for dir in input_path_dir:
            if dir == 'tmp_sort_dir':
                continue
            # 前图像类型文件路径
            dir_path = os.path.join(self.input_path, dir)
            if os.path.isdir(dir_path):
                Adir_list = os.listdir(dir_path)
                for Adir in Adir_list:
                    Adir_path = os.path.join(dir_path, Adir)
                    if os.path.isdir(Adir_path):
                        # 后每个A号文件路径
                        output = os.path.join(output_path, dir, Adir)
                        os.makedirs(output, exist_ok=True)
                        file_list = os.listdir(Adir_path)
                        for file in file_list:
                            file_path = os.path.join(Adir_path, file)
                            if os.path.isfile(file_path):
                                os.link(file_path, os.path.join(output, file))

    def move_output(self, correct, error):
        os.makedirs(os.path.join(self.output_path, 'correct'), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'error'), exist_ok=True)
        for i in correct:
            shutil.move(os.path.join(self.output_path, i), os.path.join(self.output_path, 'correct', i))
        for j in error:
            shutil.move(os.path.join(self.output_path, j), os.path.join(self.output_path, 'error', j))

    def get_folder_all_Anumber(self):
        Anumber_list = []
        type_dirs = os.listdir(self.input_path)
        for type_dir in type_dirs:
            type_dir_path = os.path.join(self.input_path, type_dir)
            if os.path.isdir(type_dir_path):
                dir_list = os.listdir(type_dir_path)
                for dir in dir_list:
                    if str(dir.split('__')[0]).startswith('A'):
                        Anumber_list.append(dir.split('__')[0])
        Anumber_list = list(set(Anumber_list))
        return Anumber_list

    def fix_image_type_sort(self):
        Anumber_list = self.get_folder_all_Anumber()
        os.makedirs(os.path.join(self.output_path, 'correct'), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'error'), exist_ok=True)
        for Anumber in Anumber_list:
            correct_list = []
            error_list = []
            same_Anumber_dir_list = []
            image_time_list = []
            try:
                anumbers, index_list = self._matchfile(self.output_path, Anumber)
                for anumber in anumbers:
                    # A号文件夹绝对路径
                    dir_path = anumber
                    if os.path.isdir(dir_path):
                        same_Anumber_dir_list.append(dir_path)
                        file_name = anumber.split('__')[1:]
                        file_name = '__'.join(file_name)
                        file_path = os.path.join(dir_path, file_name + '.json')
                        if os.path.isfile(file_path):
                            with open(file_path, 'r', encoding='utf8') as fp:
                                json_data = json.load(fp)
                                if type(json_data) == list:
                                    image_time = json_data[0]['0008|0032']
                                    image_time_list.append(image_time)
                                elif type(json_data) == dict:
                                    image_time = json_data['0008|0032']
                                    image_time_list.append(image_time)
                flag = True
                un_image_time_list = image_time_list
                if un_image_time_list:
                    if len(index_list) == 1:
                        pass
                    elif len(index_list) == 2:
                        if un_image_time_list[1] >= un_image_time_list[0]:
                            pass
                        else:
                            flag = False
                    else:
                        for i in range(len(index_list) - 1):
                            if un_image_time_list[i + 1] >= un_image_time_list[i]:
                                pass
                            else:
                                flag = False
                if flag:
                    correct_list += same_Anumber_dir_list
                else:
                    error_list += same_Anumber_dir_list

                for c_dir_index in range(len(correct_list)):
                    dir_path = correct_list[c_dir_index].split('/')
                    dir_path.insert(-2, 'correct')
                    updata_type = dir_path[-2]
                    moved_dir_path = '/'.join(dir_path)
                    file_name = dir_path[-1].split('__')[1:]
                    file_name = '__'.join(file_name)
                    update_dir_name = dir_path[-1].split('__')
                    if update_dir_name[2] == 'nan':
                        update_dir_name[2] = updata_type
                    else:
                        update_dir_name[2] = update_dir_name[2] + updata_type
                    update_dir_name = '__'.join(update_dir_name)
                    update_file_name = update_dir_name.split('__')[1:]
                    update_file_name = '__'.join(update_file_name)
                    shutil.move(correct_list[c_dir_index], moved_dir_path)
                    os.rename(os.path.join(moved_dir_path, file_name + '.json'),
                              os.path.join(moved_dir_path, update_file_name + '.json'))
                    os.rename(os.path.join(moved_dir_path, file_name + '.nii.gz'),
                              os.path.join(moved_dir_path, update_file_name + '.nii.gz'))
                    update_dir_path = correct_list[c_dir_index].split('/')[:-1]
                    update_dir_path.insert(-1, 'correct')
                    update_dir_path = '/'.join(update_dir_path)
                    os.rename(moved_dir_path, os.path.join(update_dir_path, update_dir_name))

                for e_dir in error_list:
                    move_dir = e_dir.split('/')
                    move_dir.insert(-2, 'error')
                    move_dir = '/'.join(move_dir)
                    shutil.move(e_dir, move_dir)
            except Exception as e:
                print(Anumber, e)

    def run(self, input_path, output_path, reference_head, reference_foot, no_reference, json_name,
            fix_image_type=False, **kwargs):
        self.input_path = input_path
        if fix_image_type:
            self.link_saves(output_path)
            self.fix_image_type_sort()
        else:
            self.link_save(output_path)
            all_Anumber = self.get_all_file_Anumber()
            for Anumber in all_Anumber:
                reference_head = reference_head.split(',')
                reference_foot = reference_foot.split(',')
                no_reference = no_reference.split(',')
                file_list = self.get_same_Anumber_imagefile(Anumber)
                try:
                    time_sort = self.image_time_sort(file_list)
                    type_list = self.get_same_Anumber_image_type(time_sort, json_name)
                    correct_list, error_list = self.image_type_sort(time_sort, type_list, reference_head,
                                                                    reference_foot,
                                                                    no_reference)
                    self.move_output(correct_list, error_list)
                    self.update_image_type(correct_list, json_name)
                    self.update_sorted_image_type(no_reference, json_name)
                except Exception as e:
                    print(Anumber, e)
        print('图像排序后输出的文件夹：', self.output_path)


# CT MR图像时间，类型排序
class NewSortImageName:
    def __init__(self):
        self.input_path = None
        self.output_path = None

    def get_folder_all_Anumber(self, input_path: str):
        Anumber_list = []
        type_dirs = os.listdir(input_path)
        for type_dir in type_dirs:
            type_dir_path = os.path.join(input_path, type_dir)
            if os.path.isdir(type_dir_path):
                dir_list = os.listdir(type_dir_path)
                for dir in dir_list:
                    if str(dir.split('__')[0]).startswith('A'):
                        Anumber_list.append(dir.split('__')[0])
        Anumber_list = list(set(Anumber_list))
        return Anumber_list

    def get_all_same_anumber_file(self, input_path, Anumber):
        res = []
        folders = os.listdir(input_path)
        for folder in folders:
            folder_path = os.path.join(input_path, folder)
            if Anumber in folder:
                if os.path.isdir(folder_path):
                    res.append(folder_path)
        return res

    def image_time_sort(self, input_list: list):
        image_time_list = []
        image_tag_list = []
        for folder_path in input_list:
            folder_name = folder_path.split('/')[-1]
            file_name_list = folder_name.split('__')[1:]
            file_name = '__'.join(file_name_list)
            json_path = os.path.join(folder_path, file_name + '.json')
            with open(json_path, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
            image_time = json_data[0]['0008|0032']
            image_tag = json_data[0]['0008|0033']
            image_time_list.append(image_time)
            image_tag_list.append(image_tag)
        np_argsort_index = list(np.argsort(image_time_list))
        sort_index_list = sorted(image_time_list)
        tmp_list = []
        for i in image_time_list:
            if image_time_list.count(i) > 1:
                tmp_list.append(i)
        list1 = []
        for j in set(tmp_list):
            for n in range(len(sort_index_list)):
                if sort_index_list[n] == j:
                    list1.append(n)
            list2 = []
            for z in list1:
                list2.append(image_tag_list[np_argsort_index[z]])
            np_sort_index_list2 = list(np.argsort(list2))
            for res_index in list1:
                sort_index_list[res_index] = np_sort_index_list2[0]
                np_sort_index_list2.pop(0)
        res = []
        for r in np_argsort_index:
            res.append(input_list[r])
        return res

    def get_image_time(self, input_path):
        folder_path = input_path
        folder_name = folder_path.split('/')[-1]
        file_name_list = folder_name.split('__')[1:]
        file_name = '__'.join(file_name_list)
        json_path = os.path.join(folder_path, file_name + '.json')
        with open(json_path, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
        image_time = json_data[0]['0008|0032']
        image_tag = json_data[0]['0008|0033']
        return image_time, image_tag

    def update_correct_name(self, input_list: list):
        count = 1
        res = []
        for i in input_list:
            image_type_list = i.split('/')
            image_type = image_type_list[-2] + '-%s' % count
            dir_name = image_type_list[-1]
            dir_name_list = dir_name.split('__')
            dir_name_list[2] = image_type
            dir_name = '__'.join(dir_name_list)
            image_type_list[-1] = dir_name
            image_type_list.insert(-2, 'correct')
            tmp = '/'.join(image_type_list)
            res.append(tmp)
            count += 1
        return res

    def update_error_name(self, input_list):
        res = []
        for i in input_list:
            folder_path_list = i.split('/')
            folder_path_list.insert(-2, 'error')
            folder_path = '/'.join(folder_path_list)
            res.append(folder_path)
        return res

    def get_file_name(self, folder_path: str):
        file_name_list = folder_path.split('/')[-1]
        file_name = file_name_list.split('__')[1:]
        file_name = '__'.join(file_name)
        return file_name

    def link_correct(self, old_list: list, new_list: list):
        for i in range(len(old_list)):
            old_file_name = self.get_file_name(old_list[i])
            new_file_name = self.get_file_name(new_list[i])
            os.makedirs(new_list[i])
            file_list = os.listdir(old_list[i])
            for file in file_list:
                file_path = os.path.join(old_list[i], file)
                new_file_path = os.path.join(new_list[i], file)
                os.link(file_path, new_file_path)
                os.rename(os.path.join(new_list[i], old_file_name + '.nii.gz'),
                          os.path.join(new_list[i], new_file_name + '.nii.gz'))
                os.rename(os.path.join(new_list[i], old_file_name + '.nii.gz'),
                          os.path.join(new_list[i], new_file_name + '.json'))

    def link_error(self, old_list: list, new_list: list):
        for i in range(len(old_list)):
            os.makedirs(new_list[i])
            file_list = os.listdir(old_list[i])
            for file in file_list:
                file_path = os.path.join(old_list[i], file)
                new_file_path = os.path.join(new_list[i], file)
                os.link(file_path, new_file_path)

    def fix_image_type_sort(self):
        pass
        # Anumber_list = self.get_folder_all_Anumber()
        # os.makedirs(os.path.join(self.output_path, 'correct'), exist_ok=True)
        # os.makedirs(os.path.join(self.output_path, 'error'), exist_ok=True)
        # for Anumber in Anumber_list:
        #     correct_list = []
        #     error_list = []
        #     same_Anumber_dir_list = []
        #     image_time_list = []
        #     try:
        #         anumbers, index_list = self._matchfile(self.output_path, Anumber)
        #         for anumber in anumbers:
        #             # A号文件夹绝对路径
        #             dir_path = anumber
        #             if os.path.isdir(dir_path):
        #                 same_Anumber_dir_list.append(dir_path)
        #                 file_name = anumber.split('__')[1:]
        #                 file_name = '__'.join(file_name)
        #                 file_path = os.path.join(dir_path, file_name + '.json')
        #                 if os.path.isfile(file_path):
        #                     with open(file_path, 'r', encoding='utf8') as fp:
        #                         json_data = json.load(fp)
        #                         if type(json_data) == list:
        #                             image_time = json_data[0]['0008|0032']
        #                             image_time_list.append(image_time)
        #                         elif type(json_data) == dict:
        #                             image_time = json_data['0008|0032']
        #                             image_time_list.append(image_time)
        #         flag = True
        #         un_image_time_list = image_time_list
        #         if un_image_time_list:
        #             if len(index_list) == 1:
        #                 pass
        #             elif len(index_list) == 2:
        #                 if un_image_time_list[1] >= un_image_time_list[0]:
        #                     pass
        #                 else:
        #                     flag = False
        #             else:
        #                 for i in range(len(index_list) - 1):
        #                     if un_image_time_list[i + 1] >= un_image_time_list[i]:
        #                         pass
        #                     else:
        #                         flag = False
        #         if flag:
        #             correct_list += same_Anumber_dir_list
        #         else:
        #             error_list += same_Anumber_dir_list
        #
        #         for c_dir_index in range(len(correct_list)):
        #             dir_path = correct_list[c_dir_index].split('/')
        #             dir_path.insert(-2, 'correct')
        #             updata_type = dir_path[-2]
        #             moved_dir_path = '/'.join(dir_path)
        #             file_name = dir_path[-1].split('__')[1:]
        #             file_name = '__'.join(file_name)
        #             update_dir_name = dir_path[-1].split('__')
        #             if update_dir_name[2] == 'nan':
        #                 update_dir_name[2] = updata_type
        #             else:
        #                 update_dir_name[2] = update_dir_name[2] + updata_type
        #             update_dir_name = '__'.join(update_dir_name)
        #             update_file_name = update_dir_name.split('__')[1:]
        #             update_file_name = '__'.join(update_file_name)
        #             shutil.move(correct_list[c_dir_index], moved_dir_path)
        #             os.rename(os.path.join(moved_dir_path, file_name + '.json'),
        #                       os.path.join(moved_dir_path, update_file_name + '.json'))
        #             os.rename(os.path.join(moved_dir_path, file_name + '.nii.gz'),
        #                       os.path.join(moved_dir_path, update_file_name + '.nii.gz'))
        #             update_dir_path = correct_list[c_dir_index].split('/')[:-1]
        #             update_dir_path.insert(-1, 'correct')
        #             update_dir_path = '/'.join(update_dir_path)
        #             os.rename(moved_dir_path, os.path.join(update_dir_path, update_dir_name))
        #
        #         for e_dir in error_list:
        #             move_dir = e_dir.split('/')
        #             move_dir.insert(-2, 'error')
        #             move_dir = '/'.join(move_dir)
        #             shutil.move(e_dir, move_dir)
        #     except Exception as e:
        #         print(Anumber, e)


# 图像重采样
class Resample:
    def _resample_image(self, model_image, region_image):
        """
        获得方向一致的模型
        :param itk_image:
        :return:
        """
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetOutputOrigin(region_image.GetOrigin())
        resampler.SetOutputSpacing(region_image.GetSpacing())
        resampler.SetSize(region_image.GetSize())
        resampler.SetOutputDirection(region_image.GetDirection())
        new_model_image = resampler.Execute(model_image)
        return new_model_image


# 批处理复制json文件
class BatchCopyJson:

    def _matchfile(self, input_folder, pattern):
        file_names = os.listdir(input_folder)
        names = list(filter(lambda s: re.findall(pattern, s), file_names))
        if len(names) == 0:
            raise Exception('未找到匹配文件！')
        elif len(names) > 1:
            raise Exception('匹配文件数大于1！')
        elif len(names) == 1:
            path = os.path.join(input_folder, names[0])
            return path

    def run(self, input_path, output_path, json_pattern, **kwargs):
        if not output_path:
            output_path = os.path.join(input_path, 'json_file')
        else:
            output_path = os.path.join(output_path, 'json_file')
        dirname_list = os.listdir(input_path)
        for dirname in dirname_list:
            dir = os.path.join(input_path, dirname)
            if os.path.isdir(dir):
                json_path = self._matchfile(dir, json_pattern)
                p, json_file_name = os.path.split(json_path)
                output = os.path.join(output_path, dirname)
                os.makedirs(output, exist_ok=True)
                shutil.copy(json_path, os.path.join(output, json_file_name))
        print('复制json文件操作完成，输出路径：', output_path)


# softmax值计算类
class SoftMax:
    def __init__(self):
        pass

    def _matchfile(self, input_folder, pattern):
        file_names = os.listdir(input_folder)
        names = list(filter(lambda s: re.findall(pattern, s), file_names))
        if len(names) == 0:
            raise Exception('未找到匹配文件！')
        elif len(names) > 1:
            raise Exception('匹配文件数大于1！')
        elif len(names) == 1:
            path = os.path.join(input_folder, names[0])
            return path

    def run(self, input_path, output_csv, file_pattern, **kwargs):
        if not output_csv:
            output_csv = os.path.join(input_path, 'sotfmax.csv')
        else:
            p, f = os.path.split(output_csv)
            os.makedirs(p, exist_ok=True)
        dir_names = os.listdir(input_path)
        for dir in dir_names:
            dir_path = os.path.join(input_path, dir)
            if os.path.isdir(dir_path):
                file_path = ''
                try:
                    file_path = os.path.join(input_path, self._matchfile(dir_path, file_pattern))
                except:
                    pass
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf8') as fp:
                        data = fp.read()
                        tmp_list = list(data.split(','))
                        for ind in range(len(tmp_list)):
                            tmp_list[ind] = float(tmp_list[ind])
                        scores = np.array(tmp_list)
                        scores -= np.max(scores)
                        p = np.exp(scores) / np.sum(np.exp(scores))
                        p = [float(i) for i in p]
                        # out_name = input_path.split('/')[-1]
                        p.insert(0, dir)
                        with open(output_csv, 'a', encoding='utf8') as tf:
                            csv_writer = csv.writer(tf)
                            csv_writer.writerow(p)
        print('softmax计算完成！输出目录：', output_csv)


# 头部CT MR随访数据刚性配准
class RigidRegistration:
    def __init__(self):
        self.input_path = None
        self.output_path = None
        self.fix_image = None

    def get_correct_image(self, dir):
        from smartimage.functions.registration import ImagePositionCorrector
        input_path = self.input_path
        name = dir.split('__')[1:]
        name = '__'.join(name)
        dir_path = os.path.join(input_path, dir)
        image_name = name + '.nii.gz'
        json_name = name + '.json'
        image_path = os.path.join(dir_path, image_name)
        json_path = os.path.join(dir_path, json_name)
        image = sitk.ReadImage(image_path)
        # last_position = [-125.000, -128.693, 30.378]
        last_position = self.get_last_position(json_path)
        new_image = ImagePositionCorrector.get_correct_image(image, last_position)
        return new_image

    def get_last_position(self, json_path):
        import json
        with open(json_path, 'r', encoding='utf8') as f:
            metas = json.load(f)
        last_position_str = metas[-1]['0020|0032'].split('\\')
        last_position = list(map(float, last_position_str))
        return last_position

    def get_rigid_registration_3d_transform(self, dirname, new_image):
        from smartimage.functions.registration import get_rigid_registration_3d_transform
        input_path = self.input_path
        dir_path = os.path.join(input_path, dirname)
        file_name = dirname.split('__')[1:]
        image_name = '__'.join(file_name) + '.nii.gz'
        image_path = os.path.join(dir_path, image_name)
        MOVED_IMAGE = os.path.join(self.output_path, dirname, image_name)
        moving_image = sitk.Cast(new_image, sitk.sitkFloat32)
        os.makedirs(os.path.join(self.output_path, dirname), exist_ok=True)
        # 调整窗宽窗位
        fixed_image = self.fix_image
        if 'CT' in image_name:
            fixed_image = sitk.Clamp(self.fix_image, lowerBound=-300, upperBound=300)
            moving_image = sitk.Clamp(moving_image, lowerBound=-300, upperBound=300)
        # 获取刚性配准参数
        final_transform = get_rigid_registration_3d_transform(fixed_image, moving_image)
        # 将配准参数应用于具体图像
        moving_resampled = sitk.Resample(moving_image, fixed_image, final_transform, sitk.sitkLinear, 0.0,
                                         moving_image.GetPixelID())
        sitk.WriteImage(moving_resampled, MOVED_IMAGE)

    def run(self, input_path, fix, output_path=None, **kwargs):
        fix_image = sitk.ReadImage(fix, sitk.sitkFloat32)
        self.fix_image = fix_image
        self.input_path = input_path
        if not output_path:
            output_path = os.path.join(input_path, 'registration_after')
        self.output_path = output_path
        Anumber_dirnames = os.listdir(input_path)
        os.makedirs(output_path, exist_ok=True)
        for dirname in Anumber_dirnames:
            new_image = self.get_correct_image(dirname)
            self.get_rigid_registration_3d_transform(dirname=dirname, new_image=new_image)


# 异常值统计主程序
# def main(input_path, output_path, output_file_name, **kwargs):
#     abnormalprocess = AbnormalProcess()
#     sheetnames = abnormalprocess.get_sheet_from_excel(input_path)
#     output_file = os.path.join(output_path, output_file_name)
#     for sheetname in sheetnames:
#         dataframe = pd.read_excel(input_path, sheetname=sheetname)
#         res_dataframe = abnormalprocess.add_tail_data_description(dataframe)
#         dataframe_max_index = abnormalprocess.get_max_index(dataframe)
#         res_dataframe_max_index = abnormalprocess.get_max_index(res_dataframe)
#         for column in dataframe.columns[2:]:
#             index = list(res_dataframe.columns).index(column)
#             res_dataframe.insert(index + 1, column + '.Abnormal', np.nan)
#             input_series = dataframe.loc[:, column]
#             tail_data_list = abnormalprocess.caculate_tail_data(input_series)
#             res_dataframe.loc[:, column] = list(dataframe.loc[:, column]).__add__(tail_data_list)
#             if kwargs.get('column_pattern') == 'sigma':
#                 test_list = abnormalprocess.n_sigma(int(kwargs['n']), input_series)
#                 res_dataframe.loc[:dataframe_max_index, column + '.Abnormal'] = test_list
#                 res_dataframe.loc[res_dataframe_max_index, column + '.Abnormal'] = abnormalprocess.abnormal_sum(
#                     res_dataframe.loc[:, column + '.Abnormal'])
#             elif kwargs.get('column_pattern') == 'parcentile':
#                 test_list = abnormalprocess.percentile_range(int(kwargs['col_percentile_upper']),
#                                                              int(kwargs['col_percentile_lower']), input_series)
#                 res_dataframe.loc[:dataframe_max_index, column + '.Abnormal'] = test_list
#                 res_dataframe.loc[res_dataframe_max_index, column + '.Abnormal'] = abnormalprocess.abnormal_sum(
#                     res_dataframe.loc[:, column + '.Abnormal'])
#         row_res_list = []
#         if kwargs['row_pattern'] == 'mean':
#             for i in dataframe.index.values:
#                 row_res_list.append(dataframe.iloc[i, 2:].mean())
#         elif kwargs['row_pattern'] == 'median':
#             for i in dataframe.index.values:
#                 row_res_list.append(dataframe.loc[i, 2:].median())
#         elif kwargs['row_pattern'] == 'percentile':
#             for i in dataframe.index.values:
#                 row_res_list.append(dataframe.loc[i, 2:].percentile(kwargs['row_percemtile_number']))
#         row_res_series = pd.Series(row_res_list)
#         row_res_tail_list = abnormalprocess.caculate_tail_data(row_res_series)
#         res_dataframe.loc[:, 'RowSimpleExamine'] = list(row_res_list).__add__(row_res_tail_list)
#         row_abnormal_list = []
#         if kwargs['row_abnormal_pattern'] == 'sigma':
#             row_abnormal_list = abnormalprocess.n_sigma(kwargs['row_n'], row_res_series)
#         elif kwargs['row_abnormal_pattern'] == 'percentile':
#             row_abnormal_list = abnormalprocess.percentile_range(kwargs['row_percentile_upper'],
#                                                                  kwargs['row_percentile_lower'], row_res_series)
#         res_dataframe.loc[:dataframe_max_index, 'RowSimpleExamine.Abnormal'] = row_abnormal_list
#         res_dataframe.loc[res_dataframe_max_index, 'RowSimpleExamine.Abnormal'] = abnormalprocess.abnormal_sum(
#             res_dataframe.loc[:, 'RowSimpleExamine.Abnormal'])
#         a = res_dataframe.iloc[:, 1].count()
#         res_dataframe.iloc[abnormalprocess.get_max_index(res_dataframe.iloc[:, 1]), 1] = a
#         res_dataframe = res_dataframe.reset_index()
#         res_dataframe = res_dataframe.drop(['index'], axis=1)
#         if os.path.exists(output_file):
#             writer = pd.ExcelWriter(output_file, engine='openpyxl')
#             book = load_workbook(output_file)
#             writer.book = book
#             res_dataframe.to_excel(writer, sheet_name=sheetname, index=False)
#             writer.save()
#         else:
#             writer = pd.ExcelWriter(output_file)
#             res_dataframe.to_excel(writer, sheet_name=sheetname, index=False)
#             writer.save()
#     print('异常值excel表图输出路径：', output_file)
'-----'
# ['c:\\Users\\SMIT\\Desktop\\test1\\1_WholeAbdomen_NoC\\A002928265__CT__nan__5__P10961518__A002928265__3__ABDOMEN5.0B30f']
if __name__ == '__main__':
    input_path = r'c:\Users\SMIT\Desktop\test1'
    s = NewSortImageName()
    all_Anumber = s.get_folder_all_Anumber(input_path)
    image_type_folders = os.listdir(input_path)
    image_type_folder_list = os.listdir(input_path)
    for number in all_Anumber:
        correct_list = []
        update_list = []
        error_list = []
        for image_type_folder in image_type_folder_list:
            image_type_path = os.path.join(input_path, image_type_folder)
            if os.path.isdir(image_type_path):
                folder_list = s.get_all_same_anumber_file(image_type_path, str(number))
                res = s.image_time_sort(folder_list)
                update_list.append(res)
        print(update_list)
        if len(update_list) == 1:
            correct_list = update_list
        elif len(update_list) > 1:
            for i in range(len(update_list) - 1):
                before_image_time, before_image_time_tag = s.image_time_sort(update_list[i][-1])
                after_image_time, after_image_time_tag = s.image_time_sort(update_list[i + 1][-1])
                if before_image_time > after_image_time:
                    error_list = update_list
                elif before_image_time == after_image_time:
                    if before_image_time_tag < after_image_time_tag:
                        correct_list = update_list
                    else:
                        error_list = update_list
                else:
                    error_list = update_list

        for j in correct_list:
            correct_folder_list = s.update_correct_name(j)
            s.link_correct(j, correct_folder_list)
        for k in error_list:
            error_folder_list = s.update_error_name(k)
            s.link_error(k, error_folder_list)
