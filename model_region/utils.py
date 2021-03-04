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
        label_arr = image
        label_arr[label_arr > 1] = 1
        label_arr[label_arr < 1] = 0
        label_arr.astype(np.uint8)
        region_properties = measure.regionprops(label_arr)
        # 这里界定似乎有些模糊
        arr_centroid = region_properties[0].centroid
        arr_centroid = [round(arr_centroid[0]), round(arr_centroid[1]), round(arr_centroid[2])]
        return arr_centroid

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
        self._region_model = itk_image

    def set_model_directon(self, model_image, region_image):
        """
        获得方向一致的模型
        :param itk_image:
        :return:
        """
        model_image = sitk.ReadImage(model_image)
        itk_image = sitk.ReadImage(region_image)
        # 调整region_model方向
        resampler = sitk.ResampleImageFilter()
        resampler.SetOutputOrigin(itk_image.GetOrigin())
        resampler.SetOutputSpacing(itk_image.GetSpacing())
        resampler.SetSize(itk_image.GetSize())
        resampler.SetOutputDirection(itk_image.GetDirection())
        new_region_model = resampler.Execute(model_image)
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
        return transform_arr

    def get_after_mapping_image(self, transform_arr, region_arr):
        """
        用最大交集映射图片的区域
        :param max_intersection_arr:
        :param itk_image_arr:
        :return:
        """
        res_index_list = []
        after_mapping_arr = np.zeros((region_arr.shape[0], region_arr.shape[1], region_arr.shape[2]))
        for z in range(transform_arr.shape[0]):
            for x in range(transform_arr.shape[2]):
                for y in range(transform_arr.shape[1]):
                    if transform_arr[z][y][x] == 1:
                        res_index_list.append([z, y, x])
            for i in res_index_list:
                if region_arr[i[0]][i[1]][i[2]]:
                    after_mapping_arr[i[0]][i[1]][i[2]] = region_arr[i[0]][i[1]][i[2]]
        itk_image = sitk.GetImageFromArray(region_arr)
        image_obj = sitk.GetImageFromArray(after_mapping_arr)
        image_obj.SetSpacing(itk_image.GetSpacing())
        image_obj.SetOrigin(itk_image.GetOrigin())
        image_obj.SetDirection(itk_image.GetDirection())
        # sitk.WriteImage(image_obj, 'res.nii.gz')
        return image_obj

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
        # 调整model方向
        new_model = self.set_model_directon(self._region_model, itk_image)
        # 将image转化为array
        itk_image = sitk.ReadImage(itk_image)
        itk = sitk.ReadImage(new_model)
        model_arr = sitk.GetArrayFromImage(itk)
        region_arr = sitk.GetArrayFromImage(itk_image)
        # 缩放
        transform_arr = self.set_model_shape(model_arr, region_arr)
        # 设置外接矩形
        transfrom_rectangle_centroid = self.bounding_rectangle(transform_arr)
        region_rectangle_centroid = self.bounding_rectangle(region_arr)
        # print(transfrom_rectangle_centroid, region_rectangle_centroid, transform_arr.shape, region_arr.shape)
        # 两矩形质点坐标差值
        move_z_num = region_rectangle_centroid[0] - transfrom_rectangle_centroid[0]
        move_y_num = region_rectangle_centroid[1] - transfrom_rectangle_centroid[1]
        move_x_num = region_rectangle_centroid[2] - transfrom_rectangle_centroid[2]
        tmp_z_arr = np.zeros((transform_arr.shape[0], transform_arr.shape[1], transform_arr.shape[2]))
        # 根据坐标差值进行移动
        if move_z_num > 0:
            tmp_z_arr[region_rectangle_centroid[0]:, :, :] = transform_arr[transfrom_rectangle_centroid[0]: transfrom_rectangle_centroid[0] + region_arr.shape[0] - region_rectangle_centroid[0], :, :]
            tmp_z_arr[region_rectangle_centroid[0] - transfrom_rectangle_centroid[0]-1:region_rectangle_centroid[0], :, :] = transform_arr[:transfrom_rectangle_centroid[0]+1, :, :]
        elif move_z_num == 0:
            tmp_z_arr = transform_arr
        else:
            tmp_z_arr[region_rectangle_centroid[0]:region_rectangle_centroid[0] + (transform_arr.shape[0] - transfrom_rectangle_centroid[0]), :, :] = transform_arr[transfrom_rectangle_centroid[0]:, :, :]
            tmp_z_arr[:region_rectangle_centroid[0]+1, :, :] = transform_arr[transfrom_rectangle_centroid[0] - region_rectangle_centroid[0]-1: transfrom_rectangle_centroid[0], :, :]
        # print(tmp_z_arr)
        tmp_y_arr = np.zeros((transform_arr.shape[0], transform_arr.shape[1], transform_arr.shape[2]))
        if move_y_num > 0:
            tmp_y_arr[:, region_rectangle_centroid[1]:, :] = tmp_z_arr[:, transfrom_rectangle_centroid[1]: transfrom_rectangle_centroid[1] + region_arr.shape[1] - region_rectangle_centroid[1], :]
            tmp_y_arr[:, region_rectangle_centroid[1] - transfrom_rectangle_centroid[1] - 1:region_rectangle_centroid[1], :] = tmp_z_arr[:, :transfrom_rectangle_centroid[1] +1, :]
        elif move_y_num == 0:
            tmp_y_arr = tmp_z_arr
        else:
            tmp_y_arr[:, region_rectangle_centroid[1]:region_rectangle_centroid[1] + (transform_arr.shape[1] - transfrom_rectangle_centroid[1]), :] = tmp_z_arr[:, transfrom_rectangle_centroid[1]:, :]
            tmp_y_arr[:, :region_rectangle_centroid[1]+1, :] = tmp_z_arr[:, transfrom_rectangle_centroid[1] - region_rectangle_centroid[1]-1: transfrom_rectangle_centroid[1], :]
        # print(d)
        tmp_x_arr = np.zeros((transform_arr.shape[0], transform_arr.shape[1], transform_arr.shape[2]))
        if move_x_num > 0:
            tmp_x_arr[:, :, region_rectangle_centroid[2]:] = tmp_y_arr[:, :, transfrom_rectangle_centroid[2]: transfrom_rectangle_centroid[2] + region_arr.shape[2] - region_rectangle_centroid[2]]
            tmp_x_arr[:, :,
            region_rectangle_centroid[2] - transfrom_rectangle_centroid[2]-1:region_rectangle_centroid[2]] = tmp_y_arr[:, :, : transfrom_rectangle_centroid[2]+1]
        elif move_x_num == 0:
            tmp_x_arr = tmp_y_arr
        else:
            tmp_x_arr[:, :, region_rectangle_centroid[2]:region_rectangle_centroid[2] + (transform_arr.shape[2] - transfrom_rectangle_centroid[2])] = tmp_y_arr[:, :, transfrom_rectangle_centroid[2]:]
            tmp_x_arr[:, :, :region_rectangle_centroid[2]+1] = tmp_y_arr[:, :, transfrom_rectangle_centroid[2]-region_rectangle_centroid[2]-1: transfrom_rectangle_centroid[2]]
        # 获取映射后区域
        mapping_image = self.get_after_mapping_image(tmp_x_arr, region_arr)
        return mapping_image


if __name__ == '__main__':
    # 创建对象
    model_image = 'labels__alone.nii.gz'
    itk_image = 'plabels_1__images_1.nii.gz'
    labelrigister = LabelRegister()
    labelrigister.set_region_model(model_image)
    labelrigister.rigid_registration(itk_image)
