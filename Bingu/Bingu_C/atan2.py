import math


# 计算角度
class Atan2():
    def __init__(self, v1, v2):
        self.__v1 = v1
        self.__v2 = v2

    def angle(self):
        dx1 = self.__v1[2] - self.__v1[0]
        dy1 = self.__v1[3] - self.__v1[1]
        dx2 = self.__v2[2] - self.__v2[0]
        dy2 = self.__v2[3] - self.__v2[1]
        angle1 = math.atan2(dy1, dx1)
        angle1 = int(angle1 * 180 / math.pi)
        # print(angle1)
        angle2 = math.atan2(dy2, dx2)
        angle2 = int(angle2 * 180 / math.pi)
        # print(angle2)
        if angle1 * angle2 >= 0:
            included_angle = abs(angle1 - angle2)
        else:
            included_angle = abs(angle1) + abs(angle2)
            if included_angle > 180:
                included_angle = 360 - included_angle
        return included_angle


# if __name__ == '__main__':
    # atan2 = Atan2()
