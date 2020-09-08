import math
import random


class CaculateAngle():
    # 三角形三条边求角度
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
    def caculate_from_line(self, point_A, point_B, point_C):
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
    def caculate_from_points(self, line_regression_line_a, line_regression_line_b):
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
        return self.caculate_from_line(point_A, point_B, point_C)
