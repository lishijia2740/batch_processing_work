import SimpleITK as sitk
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
    def intersection(cls, arr1, arr2, *args):
        """
        所有arr的交集
        :param arr1:
        :param arr2:
        :param args:
        :return:
        """
        arr1 = cls._to_binary(arr1)
        arr2 = cls._to_binary(arr2)
        arrs_sum = arr1 + arr2
        for other_arr in args:
            arrs_sum += cls._to_binary(other_arr)
        arrs_sum[arrs_sum == 1] = 0
        arrs_sum[arrs_sum > 1] = 1
        res = arrs_sum.astype('uint8')
        return res

    @classmethod
    def difference(cls, arr1, arr2):
        """
        第一个arr的差集
        :param arr1:
        :param arr2:
        :return:
        """
        arr1 = cls._to_binary(arr1)
        arr2 = cls._to_binary(arr2)
        arrs_sum = arr1 + arr2
        arrs_sum[arrs_sum > 1] = 3
        tmp_arr = arrs_sum.astype('uint8')
        if np.sum(tmp_arr == 3):
            tmp_arr = tmp_arr - arr2
            tmp_arr = tmp_arr + (arr1 + 1)
            tmp_arr[tmp_arr == 4] = 1
            tmp_arr[tmp_arr == 1] = 0
            tmp_arr[tmp_arr == 3] = 1
            res = tmp_arr
            return res
        else:
            tmp_arr[:] = 0
            return tmp_arr


        # arr1[arr1 > 1] = 2
        # arr1[arr1 < 1] = 0
        # arr2[arr2 > 1] = 1
        # arr2[arr2 < 1] = 0
        # res = arr1 - arr2
        # res[res == 1] = 0
        # res[res == 2] = 1
        # res = cls.complement(res)
        # return res

    @classmethod
    def complement(cls, arr):
        """
        绝对补集 除了那个区域以外的区域
        :param label:
        :return:
        """
        arr = cls._to_binary(arr)
        arr[arr == 1] = 2
        arr[arr == 0] = 1
        arr[arr == 2] = 0
        ret = arr.astype('uint8')
        return ret

    @classmethod
    def xor(cls, arr1, arr2):
        arr1 = cls._to_binary(arr1)
        arr2 = cls._to_binary(arr2)
        sum_arr = arr1 + arr2
        if np.sum(sum_arr == 2):
            sum_arr[sum_arr > 1] = 0
            ret = sum_arr.astype('uint8')
            return ret
        else:
            arr1[:] = 0
            return arr1


class LabelOperate:
    """
    对SimpleITK image对象的集合操作, label必须为整形
    """

    @classmethod
    def union(cls, label1, label2, *args):
        """
        :param label1: sitk.Image
        :param label2: sitk.Image
        :param args: [sitk.Image...]
        :return: sitk.Image
        """
        label1 = sitk.ReadImage(label1)
        label2 = sitk.ReadImage(label2)
        label1_arr = sitk.GetArrayFromImage(label1)
        label2_arr = sitk.GetArrayFromImage(sitk.Resample(label2, label1))
        other_label_arrs = [sitk.GetArrayFromImage(sitk.Resample(sitk.ReadImage(label), label1)) for label in args]
        binary_arr = ArraySetOperate.union(label1_arr, label2_arr, *other_label_arrs)
        label_ret = sitk.GetImageFromArray(binary_arr)
        label_ret.SetSpacing(label1.GetSpacing())
        label_ret.SetDirection(label1.GetDirection())
        label_ret.SetOrigin(label1.GetOrigin())
        sitk.WriteImage(label_ret, '/private/tmp/new_u.nii.gz')
        return label_ret

    @classmethod
    def difference(cls, label1, label2):
        label1 = sitk.ReadImage(label1)
        label2 = sitk.ReadImage(label2)
        label1_arr = sitk.GetArrayFromImage(label1)
        label2_arr = sitk.GetArrayFromImage(sitk.Resample(label2, label1))
        binary_arr = ArraySetOperate.difference(label1_arr, label2_arr)
        label_ret = sitk.GetImageFromArray(binary_arr)
        label_ret.SetSpacing(label1.GetSpacing())
        label_ret.SetDirection(label1.GetDirection())
        label_ret.SetOrigin(label1.GetOrigin())
        sitk.WriteImage(label_ret, '/private/tmp/new_d.nii.gz')
        return label_ret

    @classmethod
    def intersection(cls, label1, label2, *args):
        label1 = sitk.ReadImage(label1)
        label2= sitk.ReadImage(label2)
        label1_arr = sitk.GetArrayFromImage(label1)
        label2_arr = sitk.GetArrayFromImage(sitk.Resample(label2, label1))
        other_label_arrs = [sitk.GetArrayFromImage(sitk.Resample(label, label1)) for label in args]
        binary_arr = ArraySetOperate.intersection(label1_arr, label2_arr, *other_label_arrs)
        label_ret = sitk.GetImageFromArray(binary_arr)
        label_ret.SetSpacing(label1.GetSpacing())
        label_ret.SetDirection(label1.GetDirection())
        label_ret.SetOrigin(label1.GetOrigin())
        sitk.WriteImage(label_ret, '/private/tmp/new_i.nii.gz')
        return label_ret

    @classmethod
    def complement(cls, label):
        """
        绝对补集 除了那个区域以外的区域
        :param label:
        :return:
        """
        label = sitk.ReadImage(label)
        label1_arr = sitk.GetArrayFromImage(label)
        binary_arr = ArraySetOperate.complement(label1_arr)
        label_ret = sitk.GetImageFromArray(binary_arr)
        label_ret.SetSpacing(label.GetSpacing())
        label_ret.SetDirection(label.GetDirection())
        label_ret.SetOrigin(label.GetOrigin())
        sitk.WriteImage(label_ret, '/private/tmp/new_c.nii.gz')
        return label_ret

    @classmethod
    def xor(cls, label1, label2):
        label1 = sitk.ReadImage(label1)
        label2 = sitk.ReadImage(label2)
        label1_arr = sitk.GetArrayFromImage(label1)
        label2_arr = sitk.GetArrayFromImage(sitk.Resample(label2, label1))
        binary_arr = ArraySetOperate.xor(label1_arr, label2_arr)
        label_ret = sitk.GetImageFromArray(binary_arr)
        label_ret.SetSpacing(label1.GetSpacing())
        label_ret.SetDirection(label1.GetDirection())
        label_ret.SetOrigin(label1.GetOrigin())
        sitk.WriteImage(label_ret, '/private/tmp/new_x.nii.gz')
        return label_ret


if __name__ == '__main__':
    image1 = '/private/tmp/label1.nii.gz'
    image2 = '/private/tmp/label5.nii.gz'
    image3 = '/private/tmp/label9.nii.gz'
    lot = LabelOperate()
    lot.union(image3, image1, image2)
    lot.intersection(image1, image3)
    lot.difference(image2, image3)
    lot.complement(image1)
    lot.xor(image1, image3)

