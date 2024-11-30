import requests
from time import sleep
import random
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from pythonping import ping


# 需要检测的域名列表
DOMAINS = [
    'themoviedb.org',
    'www.themoviedb.org',
    'auth.themoviedb.org',
    'tmdb.org',
    'api.tmdb.org',
    'image.tmdb.org',
    'thetvdb.com',
    'api.thetvdb.com'
]

Tmdb_Host_TEMPLATE = """# Tmdb Hosts Start
{content}

# Update time: {update_time}
# Update url: https://github.com/cnwikee/CheckTMDB/Tmdb_host
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End\n"""

def write_file(hosts_content: str, update_time: str) -> bool:
    output_doc_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__), "README_template.md")
    write_host_file(hosts_content)
    if os.path.exists(output_doc_file_path):
        with open(output_doc_file_path, "r", encoding='utf-8') as old_readme_md:
            old_hosts_content = old_readme_md.read()
            if old_hosts_content:
                old_hosts = old_hosts_content.split("```bash")[1].split("```")[0].strip()
                old_hosts = old_hosts.split("# Update time:")[0].strip()
                hosts_content_hosts = hosts_content.split("# Update time:")[0].strip()
                if old_hosts == hosts_content_hosts:
                    print("host not change")
                    return False

    with open(template_path, "r", encoding='utf-8') as temp_fb:
        template_str = temp_fb.read()
        hosts_content = template_str.format(hosts_str=hosts_content,
                                            update_time=update_time)
        with open(output_doc_file_path, "w", encoding='utf-8') as output_fb:
            output_fb.write(hosts_content)
    return True

def write_host_file(hosts_content: str) -> None:
    output_file_path = os.path.join(os.path.dirname(__file__), 'Tmdb_host')
    with open(output_file_path, "w", encoding='utf-8') as output_fb:
        output_fb.write(hosts_content)
        print("\n~最新TMDB最快IP已更新~")

def get_csrf_token(udp):
    """获取CSRF Token"""
    try:
        # 构建带有 udp 参数的 URL
        url = f'https://dnschecker.org/ajax_files/gen_csrf.php?udp={udp}'
        
        # 添加 headers
        headers = {
            'referer': 'https://dnschecker.org/country/cn/'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            csrf = response.json().get('csrf')
            print(f"获取到的CSRF Token: {csrf}")
            return csrf
        else:
            print(f"获取CSRF Token失败，HTTP状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取CSRF Token时发生错误: {str(e)}")
        return None


def get_domain_ips(domain, csrf_token, udp):
    """获取域名对应的IP列表"""
    url = f'https://dnschecker.org/ajax_files/api/364/A/{domain}?dns_key=country&dns_value=cn&v=0.36&cd_flag=1&upd={udp}'
    headers = {'csrftoken': csrf_token, 'referer':'https://dnschecker.org/country/cn/'}
    
    try:
        #print(f"\n请求URL: {url}")
        #print(f"请求Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        #print(f"响应状态码: {response.status_code}")
        #print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'ips' in data['result']:
                # 处理 ips 字符串
                ips_str = data['result']['ips']
                if '<br />' in ips_str:
                    return [ip.strip() for ip in ips_str.split('<br />') if ip.strip()]
                else:
                    # 处理单个 IP 的情况
                    return [ips_str.strip()] if ips_str.strip() else []
            else:
                print(f"获取 {domain} 的IP列表失败：返回数据格式不正确")
                return []
        else:
            print(f"获取 {domain} 的IP列表失败，HTTP状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取 {domain} 的IP列表时发生错误: {str(e)}")
        return []

def ping_ip(ip):
    """ping IP地址并返回延迟时间（毫秒），ping 3次取平均值"""
    try:
        print(f"\n开始 ping {ip}...")
        # 使用pythonping进行ping测试，增加重试次数和超时时间
        ping_result = ping(ip, count=5, timeout=3, verbose=True)
        
        print(f"Ping 结果详情：")
        print(f"- 成功状态: {ping_result.success()}")
        print(f"- 平均延迟: {ping_result.rtt_avg_ms}ms")
        
        # 检查是否超时
        if ping_result.rtt_avg_ms >= 3000:  # 超时时间 * 1000
            print(f"Ping {ip} 超时")
            return float('inf')
            
        if ping_result.success():
            avg_latency = ping_result.rtt_avg_ms
            print(f"IP: {ip} 的平均延迟: {avg_latency}ms")
            return avg_latency
        else:
            print(f"Ping {ip} 失败，无响应")
            return float('inf')
    except AttributeError as ae:
        # 忽略 packets 属性相关的错误，继续处理
        if "'ResponseList' object has no attribute 'packets'" in str(ae):
            if hasattr(ping_result, 'rtt_avg_ms') and ping_result.rtt_avg_ms < 3000:
                return ping_result.rtt_avg_ms
        print(f"Ping {ip} 属性错误: {str(ae)}")
        return float('inf')
    except Exception as e:
        print(f"Ping {ip} 时发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        return float('inf')

def find_fastest_ip(ips):
    """找出延迟最低的IP地址"""
    if not ips:
        return None
    
    fastest_ip = None
    min_latency = float('inf')
    ip_latencies = []  # 存储所有IP及其延迟
    
    for ip in ips:
        ip = ip.strip()
        if not ip:
            continue
            
        print(f"正在测试 IP: {ip}")
        latency = ping_ip(ip)
        ip_latencies.append((ip, latency))
        print(f"IP: {ip} 延迟: {latency}ms")
        
        if latency < min_latency:
            min_latency = latency
            fastest_ip = ip
            
        sleep(0.5)  # 避免过快发送ping请求
    
    # 打印所有IP的延迟情况
    print("\n所有IP延迟情况:")
    for ip, latency in ip_latencies:
        print(f"IP: {ip} - 延迟: {latency}ms")
    
    if fastest_ip:
        print(f"\n最快的IP是: {fastest_ip}，延迟: {min_latency}ms")
    
    return fastest_ip

def main():
    print("开始检测TMDB相关域名的最快IP...")
    
    # 计算 udp 参数
    udp = random.random() * 1000 + (int(time.time() * 1000) % 1000)
    
    # 获取CSRF Token
    csrf_token = get_csrf_token(udp)
    if not csrf_token:
        print("无法获取CSRF Token，程序退出")
        sys.exit(1)
    
    results = []
    
    # 处理每个域名
    for domain in DOMAINS:
        print(f"\n正在处理域名: {domain}")
        
        # 获取IP列表
        ips = get_domain_ips(domain, csrf_token, udp)
        if not ips:
            print(f"无法获取 {domain} 的IP列表，跳过该域名")
            continue
            
        # 找出最快的IP
        fastest_ip = find_fastest_ip(ips)
        if fastest_ip:
            results.append([fastest_ip, domain])
            print(f"域名 {domain} 的最快IP是: {fastest_ip}")
        else:
            print(f"未能找到 {domain} 的可用IP")
        
        sleep(1)  # 避免请求过于频繁
    
    # 保存结果到文件
    hosts_content = ""
    if results:
        for ip, domain in results:
            hosts_content += f"{ip}\t{domain}\n"
                
        update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
        hosts_content = Tmdb_Host_TEMPLATE.format(content=hosts_content, update_time=update_time)

        write_file(hosts_content, update_time)
    else:
        print("\nError: 未能正确获取解析结果。")


    

if __name__ == "__main__":
    main()
