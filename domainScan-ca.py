import argparse
import requests
from bs4 import BeautifulSoup
import re


def extract_domains(url):
    dm = url
    # 对传入的url进行处理，只要域名就行
    if "http" in str(url):
        dm = re.findall(r'https?://([^/]+)', url)[0]
        url = "https://crt.sh/?q=" + dm
    # 这里默认删除www
    elif "www." in url:
        dm = re.findall(r'www.([^/]+)', url)[0]
        url = "https://crt.sh/?q=" + dm
    else:
        url = "https://crt.sh/?q=" + url

    # 发送HTTP请求获取网页内容
    response = requests.get(url)
    response.raise_for_status()  # 如果请求失败，抛出异常

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取td标签
    domains = set()
    lis = soup.select('td TABLE td')

    for row in lis:
        row = row.get_text(separator="\n", strip=True)
        # 校验td的值
        if dm in row:
            for value in row.split("\n"):
                domains.add(value)

    # 输出去重后的域名
    return domains


def save_to_file(domains, output_file):
    # 将域名写入到指定的txt文件中
    with open(output_file, 'w') as file:
        for domain in domains:
            file.write(domain + "\n")
    print(f"域名已保存到 {output_file}")


def main():
    # 使用argparse来解析命令行参数
    parser = argparse.ArgumentParser(description='利用证书查域名')
    parser.add_argument('-u', '--url', required=True, help='需要爬取的URL')
    parser.add_argument('-o', '--output', required=False, help='指定输出文件路径')
    args = parser.parse_args()

    # 提取域名
    domains = extract_domains(args.url)

    # 排序规则：将包含 '*' 的项放到前面
    domains = sorted(domains, key=lambda x: '*' not in x)

    # 输出提取的域名
    if domains:
        print("提取到的域名:")
        for domain in domains:
            print(domain)

        # 如果指定了输出文件路径，则保存到文件
        if args.output:
            save_to_file(domains, args.output)
    else:
        print("未提取到相关域名")


if __name__ == '__main__':
    main()
