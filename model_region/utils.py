import unittest
import numpy as np
from skimage import io
import SimpleITK as sitk
from skimage import measure
import torch


def auto_change_dtype(arr):
    # TODO 性能优化
    if arr.min() < 0:
        return arr.astype('int16')
    else:
        return arr.astype('uint16')


class LabelRegister:
    """
    标签配准，主要用于人工定义的分区映射到分割好的器官上，通过手工绘制区域设定分区
    """

    def __init__(self):
        self._region_model = None

    def bounding_rectangle(self, image):
        """
        设置外接矩形
        :param image:
        :return:
        """
        label_arr = sitk.GetArrayFromImage(image)
        label_arr[label_arr > 1] = 1
        label_arr[label_arr < 1] = 0
        label_arr.astype(np.uint8)
        # print(label_arr)
        region_properties = measure.regionprops(label_arr)
        # 这里界定似乎有些模糊
        print(region_properties)
        ret = region_properties[0]['bbox_area'] * self.get_volume_of_each_pix(image)
        return ret

    def get_volume_of_each_pix(self, label):
        """
        计算体积
        :param label:
        :return:
        """
        spacing = label.GetSpacing()
        vol = 1
        for val in spacing:
            vol *= val
        return vol

    def get_model_acme(self, itk_arr):
        """
        获得模型四个顶点
        :param itk_arr:
        :return:
        """
        res_list = []
        row_list = []
        col_list = []
        for i in range(itk_arr.shape[0]):
            for x in range(itk_arr.shape[2]):
                for y in range(itk_arr.shape[1]):
                    if itk_arr[i][y][x] == 1:
                        col_list.append([i, y, x])
            left = col_list[0]
            right = col_list[-1]
            for y in range(itk_arr.shape[1]):
                for x in range(itk_arr.shape[2]):
                    if itk_arr[i][y][x] == 1:
                        row_list.append([i, y, x])
            top = col_list[0]
            bottom = col_list[-1]
            res_list = [left, right, top, bottom]
        return res_list

    def set_same_position(self, point_list):
        """
        获得平移方向和距离
        :param model_point:
        :param region_point:
        :return:
        """
        res_list = []
        print(point_list)
        for i in point_list:
                model_point = i[0]
                region_point = i[1]
                # print(model_point, region_point)
                y_diff = region_point[1] - model_point[1]
                x_diff = region_point[2] - model_point[2]
                if y_diff > 0:
                    row_move_direction = 'right'
                    row_move_number = y_diff
                else:
                    row_move_direction = 'left'
                    row_move_number = abs(y_diff)
                if x_diff > 0:
                    col_move_direction = 'bottom'
                    col_move_number = x_diff
                else:
                    col_move_direction = 'top'
                    col_move_number = abs(x_diff)
                res_list.append([row_move_direction, row_move_number, col_move_direction,
                                 col_move_number, model_point, region_point])
        return res_list

    def intersection(self, arr1, arr2, *args):
        """
        所有arr的交集
        """
        arr1 = self._to_binary(arr1)
        arr2 = self._to_binary(arr2)
        arrs_sum = arr1 + arr2
        for other_arr in args:
            arrs_sum += self._to_binary(other_arr)
        arrs_sum[arrs_sum == 1] = 0
        arrs_sum[arrs_sum > 1] = 1
        res = arrs_sum.astype('uint8')
        return res

    @staticmethod
    def _to_binary(label_arr):
        label_arr[label_arr > 1] = 1
        label_arr[label_arr < 1] = 0
        ret = label_arr.astype('uint8')
        return ret

    def label_binary_array_resize_4d(self, labels, target_shape):
        """
        用于二值化标签缩放，返回整形
        此函数经常被标签缩放调用，类似临近差值，但是不能处理多个不同值的标签,多个标签用image_array_resize_4d(imgs, target_shape, mode='nearest')
        :param labels: (c,z,y,x) 二值化数组,0-1
        :param target_shape: (z,y,x)
        :return: 二值化数组，(c,z,y,x)
        """
        labels[labels > 1] = 1
        # assert labels.max() <= 1 and labels.min() >= 0, '暂不支持标签的值含有除0和1以外的值'
        float_labels = self.image_array_resize_4d(labels, target_shape)
        float_labels[float_labels > 0.5] = 1  # float_imgs += 0.49  # 避免标签大面积缺失问题
        int_imgs = float_labels.astype('uint8')
        return int_imgs

    def label_array_resize_3d(self, label_arr, target_shape):
        """
        3维度标签缩放，支持多个数值的标签
        主要原理是把3维度标签按每个值拆分(np.unique(arr)可以查看数组有什么值)，组成4维数组，调用label_binary_array_resize_4d，再将生成的4维度数组合并为3维度数组
        :param label_arr: (z,y,x) 3维数组，整型
        :param target_shape: (z,y,x)
        :return:  (z,y,x) 3维数组，dtype为np.int16
        """
        label_arr = np.array([label_arr])
        res_arr = self.label_binary_array_resize_4d(label_arr, target_shape)[0]
        return res_arr

    def image_array_resize_4d(self, imgs, target_shape, mode='trilinear'):
        """
        用于dicom或者nii图像缩放，注意返回浮点型，需要按需处理为整型
        :param imgs: (c,z,y,x)
        :param target_shape: (z,y,x)
        :param mode: (string): algorithm used for upsampling:
                'nearest' | 'linear' | 'bilinear' | 'trilinear' | 'area'.特别注意直接用nearest会发生标签偏移的问题
        :return:浮点型，(c,z,y,x)
        """
        imgs = imgs[np.newaxis].astype(np.float)
        imgs = torch.from_numpy(imgs)
        # print(imgs)
        # https://www.cnblogs.com/wanghui-garcia/p/11399034.html
        # 这里必须ValueError: align_corners option can only be set with the interpolating modes: linear | bilinear | trilinear
        imgs = torch.nn.functional.interpolate(imgs, size=target_shape, mode=mode)  # align_corners=True没啥区别
        float_imgs = imgs.numpy()[0]
        # int_imgs = float_imgs.astype('uint8')
        return float_imgs

    def set_region_model(self, itk_image):
        """
        设置标注好的分区的label，每个区域用不同的数值表示
        :param itk_image: sitk.Image 对象
        :return:
        """
        itk_image = sitk.ReadImage(itk_image)
        self._region_model = itk_image

    def set_model_directon(self, itk_image):
        """
        获得方向一致的模型
        :param itk_image:
        :return:
        """
        itk_image = sitk.Image(itk_image)
        # 调整region_model方向
        transform = sitk.Transform()
        transform.SetIdentity()
        resampler = sitk.ResampleImageFilter()
        resampler.SetTransform(transform)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetOutputOrigin(itk_image.GetOrigin())
        resampler.SetOutputSpacing(itk_image.GetSpacing())
        resampler.SetSize(itk_image.GetSize())
        resampler.SetOutputDirection(itk_image.GetDirection())
        new_region_model = resampler.Execute(self._region_model)
        return new_region_model

    def set_model_shape(self, model_new_arr, region_arr):
        """
        获得模型形状
        :param model_new_arr:
        :param region_arr:
        :return:
        """
        transform_arr = self.label_array_resize_3d(model_new_arr,
                                                   (region_arr.shape[0], region_arr.shape[1], region_arr.shape[2]))
        # res_index_list = []
        # for transform_arr in transform_arr_list:
        #     # print(transform_arr)
        #     for z in range(transform_arr.shape[0]):
        #         for x in range(transform_arr.shape[2]):
        #             for y in range(transform_arr.shape[1]):
        #                 if transform_arr[z][y][x] == 1:
        #                     res_index_list.append([y, x])
        #         for i in res_index_list:
        #             transform_arr[z][i[0]][i[1]] = region_arr[z][i[0]][i[1]]
        return transform_arr

    def rigid_registration(self, itk_image):
        """
        标签刚性配准，将大体的器官映射到region_model对应的区域上
        第一步：将region_model方向调整到与itk_image一致
            resampler = sitk.ResampleImageFilter()
            resampler.SetOutputDirection(itk_image.GetDirection())
            new_region_model = resampler.Execute(self._region_model)
        第二步：通过缩放，移动等操作，调整region_model的大小位置，使得两者外接矩形基本重合
            外接矩形参考batch_command\djTubePositions.py 170-175行
            3d图像缩放调用smartimage.transforms.utils.label_array_resize_3d,此函数需要自行完善
        第三步： 对调整后的region_model构造sitk.Image对象，并返回
                image_obj = sitk.GetImageFromArray(image_arr)
                image_obj.SetSpacing(itk_image.GetSpacing())
                image_obj.SetOrigin(itk_image.GetOrigin())
                image_obj.SetDirection(itk_image.GetDirection())
        :param itk_image: sitk.Image 对象
        :return: sitk.Image 对象
        """
        # 调整方向
        new_region_model = self.set_model_directon(self._region_model)
        # 将image转化为array
        itk_image = sitk.ReadImage(itk_image)
        model_arr = sitk.GetArrayFromImage(new_region_model)
        region_arr = sitk.GetArrayFromImage(itk_image)
        # 缩放
        transform_arr = self.set_model_shape(model_arr, region_arr)
        # 找到模型的四个顶点
        model_acme_list = self.get_model_acme(transform_arr)
        region_acme_list = self.get_model_acme(region_arr)
        print(model_acme_list, region_acme_list)
        move_parameter_list = self.set_same_position([i for i in zip(model_acme_list, region_acme_list)])
        # 移动
        result_list = []
        for move_parameter in move_parameter_list:
            tmp_arr = np.zeros((model_arr.shape[0], model_arr.shape[1], model_arr.shape[2]))
            # print(model_new_arr)
            # 删除数组列 map(lambda x: x[1:], a)
            row_move_direction, row_move_number, col_move_direction, col_move_number, model_point, region_point = \
                move_parameter[0], move_parameter[1], move_parameter[2], move_parameter[3], move_parameter[4], \
                move_parameter[5]
            if move_parameter[0] == 'right':
                tmp_arr[:, model_point[1] + row_move_number:] = model_arr[0][:, model_point[1]:-row_move_number]
            else:
                tmp_arr[:, model_point[1] - row_move_number:-row_move_number] = model_arr[0][:, model_point[1]:]
            model_new_arr = np.zeros((model_arr.shape[1], model_arr.shape[2]))
            if col_move_direction == 'bottom':
                model_new_arr[model_point[0] + row_move_number:, :] = tmp_arr[model_point[1]:-row_move_number, :]
            else:
                model_new_arr[model_point[0] - row_move_number:-row_move_number, :] = tmp_arr[model_point[0]:, :]

            # 求最大交集
            result = self.intersection(model_new_arr, region_arr)
            print(result)
            # 求映射后的数组
            # res_index_list = []
            # for z in range(transform_arr.shape[0]):
            #     for x in range(transform_arr.shape[2]):
            #         for y in range(transform_arr.shape[1]):
            #             if transform_arr[z][y][x] == 1:
            #                 res_index_list.append([y, x])
            #     for i in res_index_list:
            #         transform_arr[z][i[0]][i[1]] = region_arr[z][i[0]][i[1]]

        # list1 = [0, 1, 2, 3, 0]
        # list2 = [0, 5, 6, 7, 8]
        # label_arr = np.array([[list1, list2]])
        # # eare = self.bounding_rectangle(a)
        # label_arr[label_arr > 1] = 1
        # label_arr[label_arr < 1] = 0
        # label_arr.astype(np.uint8)
        # # print(label_arr)
        # print(label_arr)
        # region_properties = measure.label(label_arr)
        # # 这里界定似乎有些模糊
        # print(region_properties)
        # print(self.get_volume_of_each_pix(itk_image))
        # ret = region_properties[0]['bbox_area'] * self.get_volume_of_each_pix(itk_image)
        # print(ret)


# class LabelRegisterTestCase(unittest.TestCase):
#     """
#     测试用例类
#     """
#
#     def setUp(self):
#         """
#         创建调查对象和答案
#         :return:
#         """
#         pass
#
#     def test_set_region_model(self):
#         """
#
#         :return:
#         """
#         pass
#
#     def test_rigid_registration(self):
#         """
#
#         :return:
#         """
#         pass


if __name__ == '__main__':
    # region_image = sitk.ReadImage('plabels_1__images_1.nii.gz')
    # model_1 = sitk.ReadImage('labels__1__alone.nii.gz')
    # model_2 = sitk.ReadImage('labels__2__alone.nii.gz')
    # model_1_arr = sitk.GetArrayFromImage(model_1)[:1]
    # model_2_arr = sitk.GetArrayFromImage(model_2)[:1]
    # # region_arr = sitk.GetArrayFromImage(region_image)
    # model_arr = model_1_arr + model_2_arr
    # # if model_arr[model_arr == 1]:
    # #     model_arr[model_arr == 1] += 1
    # out = sitk.GetImageFromArray(model_arr)
    # sitk.WriteImage(out, 'labels__alone.nii.gz')

    # img = sitk.ReadImage('labels__alone.nii.gz')
    # img_arr = sitk.GetArrayFromImage(img)
    # io.imshow(img_arr[0], cmap='gray')
    # io.show()

    # 构造
    # arr1 = np.zeros((1, 9, 9))
    # arr1[0][3:6, 3:6] = 1
    # print(arr1)
    # arr2 = np.zeros((1, 9, 9))
    # arr2[0][2:5, 2:5] = 1
    # arr2[0][4, 2:4] = 0
    # print(arr2)
    # io.imshow(arr1[0], cmap='gray')
    # io.show()
    # io.imshow(arr2[0], cmap='gray')
    # io.show()
    # #
    # image1 = sitk.GetImageFromArray(arr1)
    # image2 = sitk.GetImageFromArray(arr2)
    # #
    # # print(image1)
    # # print(image2)
    # sitk.WriteImage(image1, 'label__alone.nii.gz')
    # sitk.WriteImage(image2, 'model.nii.gz')

    labelrigister = LabelRegister()
    labelrigister.set_region_model('model.nii.gz')
    labelrigister.rigid_registration('label__alone.nii.gz')
