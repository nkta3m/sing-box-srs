#!/bin/bash

# 指定内容添加到文件最前面的变量
prefix_content='{
    "version": 1,
    "rules": [
        {
            "domain": ['
# 指定内容添加到文件最后面的变量
suffix_content='
           ]
        }
    ]
}'

# 循环处理每个文件
for file in *.json; do
	# 检查是否为文件
	if [ -f "$file" ]; then
		# 1. 删除以 # 开头的行
		sed -i '/^#/d' "$file"

		# 2. 删除空行
		sed -i '/^$/d' "$file"

		# 3. 对剩下的行添加双引号和逗号
		sed -i -e 's/.*/"&",/' "$file"

		# 4. 删除最后一行的逗号
		sed -i '$s/,$//' "$file"

		# 5. 在文件最前面添加指定内容
		echo "$prefix_content" | cat - "$file" >temp && mv temp "$file"

		# 6. 在文件最后添加指定内容
		echo "$suffix_content" >>"$file"
	fi
done
