import base64
import json
from urllib.parse import unquote


def parse_vmess(line: str):
    if line.startswith("vmess://"):
        line = line[len("vmess://") :]

    try:
        decoded = base64.urlsafe_b64decode(line + "=" * (-len(line) % 4)).decode(
            "utf-8"
        )
        data = json.loads(decoded)
    except Exception as e:
        print(f"[VMess] 解码失败: {e}")
        return None

    # 取 aid 映射到 alter_id，若没有则默认 0
    alter_id = int(data.get("aid", 0))

    # 获取 transport type
    valid_transports = {"HTTP", "WebSocket", "QUIC", "gRPC", "HTTPUpgrade"}
    net_type = data.get("net", "")
    if net_type not in valid_transports:
        net_type = "ws"  # 默认值

    # 构造 Sing-box 出站节点
    node = {
        "type": "vmess",
        "tag": data.get("ps", ""),
        "server": data.get("add", ""),
        "server_port": int(data.get("port", 0)),
        "uuid": data.get("id", ""),
        "alter_id": alter_id,
        "security": data.get("security", "auto"),
        "transport": {
            "type": net_type,
            "path": data.get("path", ""),
            "headers": {"Host": data.get("host", "")},
        },
    }

    # 如果有 TLS 配置的话，可以在这里加入 “tls” 字段（可根据 data 里的字段决定）
    # 例：
    # if data.get("tls") == "tls" or data.get("tls") == "1":
    #     node["tls"] = {
    #         "enabled": True,
    #         "server_name": data.get("host", ""),
    #         "disable_sni": False,
    #         "insecure": data.get("skip-cert-verify", False)
    #     }

    return node


def parse_ss(line: str):
    if not line.startswith("ss://"):
        return None
    line = line[len("ss://") :]

    tag = ""
    if "#" in line:
        line, tag = line.split("#", 1)
        tag = unquote(tag)

    if "@" in line:
        method_pwd_b64, server_part = line.split("@", 1)
        server, port = server_part.split(":")
        method_pwd = base64.urlsafe_b64decode(
            method_pwd_b64 + "=" * (-len(method_pwd_b64) % 4)
        ).decode("utf-8")
    else:
        decoded = base64.urlsafe_b64decode(line + "=" * (-len(line) % 4)).decode(
            "utf-8"
        )
        method_pwd, server_part = decoded.split("@", 1)
        server, port = server_part.split(":")

    method, password = method_pwd.split(":", 1)

    node = {
        "type": "shadowsocks",
        "tag": tag,
        "server": server,
        "server_port": int(port),
        "method": method,
        "password": password,
    }

    return node


def convert_file(input_file: str, output_file: str):
    nodes = []
    tags = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parsed = None
            if line.startswith("vmess://"):
                parsed = parse_vmess(line)
            elif line.startswith("ss://"):
                parsed = parse_ss(line)
            else:
                print(f"未知协议: {line}")
                continue

            if parsed:
                nodes.append(parsed)
                tag = parsed.get("tag")
                if tag:
                    tags.append(tag)

    # 最终输出：符合 Sing-box 出站节点格式 + tags 一节
    final = {"outbounds": nodes, "tags": tags}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=4)

    print(f"转换完成，输出保存到 {output_file}")


if __name__ == "__main__":
    input_file = "nodes.txt"
    output_file = "singbox_outbound.json"
    convert_file(input_file, output_file)
