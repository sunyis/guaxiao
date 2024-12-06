import requests
from time import sleep
import random
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from retry import retry
import socket

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

@retry(tries=3)
def get_csrf_token(udp):
    """获取CSRF Token"""
    try:
        url = f'https://dnschecker.org/ajax_files/gen_csrf.php?udp={udp}'
        headers = {
            'referer': 'https://dnschecker.org/country/cn/','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
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

@retry(tries=3)
def get_domain_ips(domain, csrf_token, udp):
    url = f'https://dnschecker.org/ajax_files/api/364/A/{domain}?dns_key=country&dns_value=cn&v=0.36&cd_flag=1&upd={udp}'
    headers = {'csrftoken': csrf_token, 'referer':'https://dnschecker.org/country/cn/','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'ips' in data['result']:
                ips_str = data['result']['ips']
                if '<br />' in ips_str:
                    return [ip.strip() for ip in ips_str.split('<br />') if ip.strip()]
                else:
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

def ping_ip(ip, port=80):
    """使用TCP连接测试IP地址的延迟（毫秒）"""
    try:
        print(f"\n开始 ping {ip}...")
        start_time = time.time()
        with socket.create_connection((ip, port), timeout=2) as sock:
            latency = (time.time() - start_time) * 1000  # 转换为毫秒
            print(f"IP: {ip} 的平均延迟: {latency}ms")
            return latency
    except Exception as e:
        print(f"Ping {ip} 时发生错误: {str(e)}")
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
            
        sleep(0.5) 
    
    print("\n所有IP延迟情况:")
    for ip, latency in ip_latencies:
        print(f"IP: {ip} - 延迟: {latency}ms")
    
    if fastest_ip:
        print(f"\n最快的IP是: {fastest_ip}，延迟: {min_latency}ms")
    
    return fastest_ip

def main():
    print("开始检测TMDB相关域名的最快IP...")
    udp = random.random() * 1000 + (int(time.time() * 1000) % 1000)
    # 获取CSRF Token
    csrf_token = get_csrf_token(udp)
    if not csrf_token:
        print("无法获取CSRF Token，程序退出")
        sys.exit(1)
    
    results = []
    for domain in DOMAINS:
        print(f"\n正在处理域名: {domain}")
        ips = get_domain_ips(domain, csrf_token, udp)
        if not ips:
            print(f"无法获取 {domain} 的IP列表，跳过该域名")
            continue
            
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
