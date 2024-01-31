#!/bin/bash

# 检查 sing-box 是否在 PATH 中，如果不在，请根据实际路径修改
SING_BOX_CMD="/usr/local/bin/sing-box"
if ! command -v "$SING_BOX_CMD" &>/dev/null; then
	echo "Error: sing-box command not found. Please update the script with the correct path."
	exit 1
fi

# 循环处理每个json文件
for json_file in *.json; do
	# 检查是否为文件
	if [ -f "$json_file" ]; then
		# 构建输出文件名（将json扩展名替换为srs）
		srs_file="${json_file%.json}.srs"

		# 执行 sing-box 命令进行转换
		"$SING_BOX_CMD" rule-set compile --output "$srs_file" "$json_file"

		echo "Converted $json_file to $srs_file"
	fi
done
