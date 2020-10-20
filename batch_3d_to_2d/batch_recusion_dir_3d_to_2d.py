import os
import SimpleITK as sitk


def recusion_dir(input_path, output_path, mark_file_name):
    list_names = os.listdir(input_path)
    for list_name in list_names:
        next_list_name = os.path.join(input_path, list_name)
        if os.path.isfile(next_list_name):
            if list_name == mark_file_name:
                count = 1
                image_arr = sitk.GetArrayFromImage(sitk.ReadImage(next_list_name))
                for n in range(image_arr.shape[0]):
                    two_d_image = sitk.GetImageFromArray(image_arr[n, :, :])
                    out_path = os.path.join(output_path, '{}-{}-{}.nii.gz'.format(next_list_name.split('/')[-2],next_list_name.split('/')[-1][:-7], count))
                    sitk.WriteImage(two_d_image, out_path)
                    count += 1
                    print(out_path)

        else:
            recusion_dir(next_list_name, output_path, mark_file_name)


def main(input_path, output_path, mark_file_name):
    if os.path.exists(output_path):
        print('文件已存在！')
    else:
        os.makedirs(output_path)
        recusion_dir(input_path, output_path, mark_file_name)


if __name__ == '__main__':
    INPUT_PATH = '/private/tmp/processed_data'
    OUTPUT_PATH = '/private/tmp/2d_to_2d'
    FILE_NAME = 'labels__1__alone.nii.gz'
    main(INPUT_PATH, OUTPUT_PATH, FILE_NAME)
