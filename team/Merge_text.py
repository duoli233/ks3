import os
import Train
def merge_two_files(file1_path, file2_path, output_file):
    # 打开输出文件，准备写入合并后的内容
    with open(output_file, 'w+', encoding='utf-8') as out_file:
        data1 = Train.read_text(file1_path)
        data2 = Train.read_text(file2_path)
        count = 0
        if len(data1) == len(data2):
            lenth = len(data1)
            while count < lenth:
                if data1[count] == "<>" or data1[count] == "< >":
                    if data2[count] == "<>" or data1[count] == "< >":
                        out_file.write(data1[count])
                    else:
                        out_file.write(data2[count])
                else:
                    out_file.write(data1[count])
                out_file.write('\n')
                count += 1

    print(f"合并完成，合并后的文件保存在 {output_file}")

# 示例用法
file1_path = 'data\\answer.txt'  # 第一个文件路径
file2_path = 'data\old_value_file\\answer\\merged_file7.txt'  # 第二个文件路径
output_file = 'data\old_value_file\\answer\merged_file.txt'  # 输出合并后的文件路径

merge_two_files(file1_path, file2_path, output_file)