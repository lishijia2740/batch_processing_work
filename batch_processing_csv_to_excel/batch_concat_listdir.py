import os
import re
import pprint


def match_nii_names(nii_names, patterns):
    matched_nii_names = []
    for name in nii_names:
        for pattern in patterns:
            names = re.findall(pattern, name)
            if len(names) == 0:
                pass
            elif len(names) == 1:
                matched_nii_names.append(names[0])
            else:
                raise ValueError('{pattern}规则只允许匹配一个文件，但是匹配到{names}，请修改规则或修改文件名'.format(
                    pattern=pattern, names=names))
    return matched_nii_names


def get_file_paths_by_regex(folder_path, *args, res_list=[], tmp_list=[], tmp_dict={}, count=0):
    dirlist = os.listdir(folder_path)
    for dirname in dirlist:
        new_path = os.path.join(folder_path, dirname)
        if os.path.isdir(new_path):
            dirlistnames = os.listdir(new_path)
            for patterns in args:
                res = match_nii_names(dirlistnames, patterns)
                for filename in res:
                    tmp_list.append(os.path.join(new_path, filename))
                if count == 0:
                    tmp_dict.update({'image_paths': tmp_list})
                    tmp_list = []
                    count += 1
                elif count == 1:
                    tmp_dict.update({'label_paths': tmp_list})
                    tmp_list = []
                    count += 1
                elif count == 2:
                    tmp_dict.update({'plabel_paths': tmp_list})
                    tmp_list = []
                    count += 1
                elif count == 3:
                    tmp_dict.update({'mask_paths': tmp_list})
                    #
                    res_list.append(tmp_dict)
                    tmp_dict = {}
                    tmp_list = []
                    count = 0

    pprint.pprint(res_list)
    return res_list


def main():
    pass


if __name__ == '__main__':
    # ‪C:\Users\SMIT\Desktop\processed_data
    # 如果images，labels，masks某个参数为None，则不输出该项的路径
    FOLDER_PATH = r'D:\project\batch_processing_work\batch_processing_csv_to_excel\processed_data\test1'
    image = ['^image.*nii.gz$']
    label = ['^label.*nii.gz$']
    mask = ['^p1label.*nii.gz']
    plabel = ['^plabel.*nii.gz$']
    get_file_paths_by_regex(FOLDER_PATH, image, label, plabel, mask)
    # match_nii_names(['images_1.nii.gz', 'labels_1.nii.gz', 'labels_2.nii.gz'], label)
