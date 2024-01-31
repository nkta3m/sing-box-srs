#!/bin/bash

# 指定的目标文件
output_file="geosite-mozilla.json"

# 循环处理每一行
while IFS= read -r line; do
	# 如果行是以#开头的，跳过
	if [[ $line == \#* ]]; then
		continue
	fi

	# 如果行的开始不是#开始的，而且不包括include，直接合并到目标文件
	if [[ $line != *include* ]]; then
		echo "$line" >>"$output_file"
		echo "Directly merged line: $line to $output_file"
	else
		# 提取文件名
		filename=$(echo "$line" | cut -d':' -f2 | awk '{gsub(/^[ \t]+|[ \t]+$/, ""); print}')

		# 检查文件是否存在
		if [ -f "$filename" ]; then
			# 合并文件内容到目标文件
			cat "$filename" >>"$output_file"
			echo "Merged content from $filename to $output_file"
		else
			echo "Warning: File $filename not found."
		fi
	fi
done <mozilla # 替换为你的输入文件的实际路径
