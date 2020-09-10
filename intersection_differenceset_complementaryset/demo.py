import numpy as np


class ArraySetOperate:
    """
    label numpy数组集合操作，必须为整型，且大小相同
    """

    @classmethod
    def union(cls, arr1, arr2, *args):
        arrs_sum = arr1 + arr2
        for other_arr in args:
            arrs_sum += other_arr
        binary_arr = cls._to_binary(arrs_sum)
        return binary_arr

    @staticmethod
    def _to_binary(label_arr):
        label_arr[label_arr > 1] = 1
        label_arr[label_arr < 1] = 0
        ret = label_arr.astype('uint8')
        return ret

    @classmethod
    def intersection(cls, arr1, arr2):
        arrs_sum = arr1 + arr2
        binary_arr = cls._to_transform(arrs_sum)
        return binary_arr

    @staticmethod
    def _to_transform(label_arr):
        label_arr[label_arr == 1] = 0
        label_arr[label_arr > 1] = 1
        ret = label_arr.astype('uint8')
        return ret

    @classmethod
    def difference(cls, arr1, arr2, *args):
        arrs_sum = arr1 + arr2
        for other_arr in args:
            arrs_sum += other_arr
        binary_arr = cls._to_replace(arrs_sum)
        binary_arr[binary_arr > 1] = 2
        res = binary_arr - arr1
        res = cls.complement(res)
        return res

    @staticmethod
    def _to_replace(label_arr):
        label_arr[label_arr == 1] = 0
        label_arr[label_arr > 1] = 2
        ret = label_arr.astype('uint8')
        return ret

    @classmethod
    def complement(cls, arr):
        """
        绝对补集 除了那个区域以外的区域
        :param label:
        :return:
        """
        arr[arr == 2] = 0
        arr[arr == 1] = 2
        arr[arr == 0] = 1
        ret = arr.astype('uint8')
        return ret


if __name__ == '__main__':
    image1 = np.zeros(shape=(4, 4))
    image2 = np.ones(shape=(4, 4))
    image1[1:3, 1:3] = 1
    aot = ArraySetOperate()
    print(aot.difference(image1, image2))
