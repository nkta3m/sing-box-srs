#!/usr/bin/env python3
import urllib.parse
import json
import re
import sys

# ----------------------------
# 配置（可通过命令行传入版本）
# ----------------------------
input_file = "ouo"  # 原始 VLESS 文件名（你已有的那个）
version = "1.11"  # 默认版本，可选 "1.11" 或 "1.12"
if len(sys.argv) >= 2:
    version = sys.argv[1]

output_file = f"singbox_selector_v{version.replace('.', '_')}.json"

# ----------------------------
# 读取原始节点
# ----------------------------
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read().strip()

# 匹配所有 vless:// 链接（支持单行或多行）
vless_links = re.findall(r"vless://[^\s]+", content)


# ----------------------------
# 节点解析函数（包含 packet_encoding）
# ----------------------------
def parse_vless(link, version="1.11"):
    parsed = urllib.parse.urlparse(link)
    uuid = parsed.username
    server = parsed.hostname
    port = parsed.port
    query = urllib.parse.parse_qs(parsed.query)

    # 获取常见字段（兼容 packetEncoding 与 packet_encoding）
    path = query.get("path", [""])[0]
    host = query.get("host", [""])[0]
    # flow = query.get("flow", [""])[0]
    transport_type = query.get("type", ["tcp"])[0]
    # packetEncoding param in links like ...&packetEncoding=xudp
    packet_encoding = query.get("packetEncoding", query.get("packet_encoding", [""]))[
        0
    ].lower()
    tag = (
        urllib.parse.unquote(parsed.fragment) if parsed.fragment else f"{server}:{port}"
    )

    # build node dict; include packet_encoding only if present
    if version == "1.11":
        node = {
            "type": "vless",
            "tag": tag,
            "server": server,
            "server_port": port,
            "uuid": uuid,
            # "flow": flow,
            "transport": {
                "type": transport_type,
                "path": path,
                "headers": {"Host": host},
            },
            "network": "tcp",
            # 按你要求：不输出 tls、skip-cert-verify、tcp_fast_open
        }
        if packet_encoding:
            node["packet_encoding"] = packet_encoding
    elif version == "1.12":
        node = {
            "type": "vless",
            "tag": tag,
            "server": server,
            "server_port": port,
            "uuid": uuid,
            "transport": {
                "type": transport_type,
                "path": path,
                "headers": {"Host": host},
            },
            "network": "tcp",
            # 按你要求：不输出 tcp_fast_open、tls
        }
        if packet_encoding:
            node["packet_encoding"] = packet_encoding
    else:
        raise ValueError("不支持的版本: " + version)

    return node


# ----------------------------
# 解析所有节点并构造最终 config
# ----------------------------
nodes = [parse_vless(link, version) for link in vless_links]
tags = [node["tag"] for node in nodes]

auto_node = {
    "tag": "♻️ 自动选择",
    "type": "urltest",
    "outbounds": tags,
    "url": "http://www.gstatic.com/generate_204",
    "interval": "5m",
    "tolerance": 50,
}
proxy_node = {"tag": "🚀 Proxy", "type": "selector", "outbounds": ["♻️ 自动选择"] + tags}

final_config = [auto_node, proxy_node] + nodes

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_config, f, ensure_ascii=False, indent=2)

print(f"转换完成，版本 {version}，文件: {output_file}")
