#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML网站导航解析器
解析MHTML文件中的网站导航结构并输出为YAML格式
"""

import re
import html
import quopri

def parse_mhtml_file(filepath):
    """解析MHTML文件并提取网站导航结构"""
    
    # 读取MHTML文件
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # 提取HTML内容部分
    html_start = content.find(b'<!DOCTYPE html>')
    html_end = content.find(b'------MultipartBoundary', html_start)
    html_content = content[html_start:html_end]
    
    # 解码quoted-printable编码的HTML
    html_text = html_content.decode('utf-8', errors='ignore')
    # URL解码特殊字符（=E6=97=A5等）
    html_text = quopri.decodestring(html_text.encode('latin1')).decode('utf-8', errors='ignore')
    
    # HTML实体解码
    html_text = html.unescape(html_text)
    
    # 查找所有分类区块
    categories = []
    
    # 查找所有 class='wa' 的div（每个分类一个）
    wa_divs = re.findall(r'<div class="wa">(.*?)</div></div>', html_text, re.DOTALL)
    
    for block in wa_divs:
        # 提取分类名称
        category_match = re.search(r'<span class="za">(.*?)</span>', block)
        if category_match:
            category_name = category_match.group(1)
            
            # 提取该分类下的所有链接
            links = []
            # 查找所有链接项：<a class="Da" href="..." 和 <span class="Ia">title</span>
            link_items = re.findall(
                r'<a class="Da" href="(.*?)"[^>]*>.*?<span class="Ia">(.*?)</span>', 
                block, 
                re.DOTALL
            )
            
            for url, title in link_items:
                links.append({
                    'title': title,
                    'url': url,
                })
            
            if links:
                categories.append({
                    'term': category_name,
                    'links': links
                })
    
    return categories


def output_yaml(categories):
    """输出YAML格式的数据"""
    for cat in categories:
        print(f'- term: {cat["term"]}')
        print('  links:')
        for link in cat['links']:
            print(f'  - title: {link["title"]}')
            print(f'    url: {link["url"]}')
            print(f'    description: ""')
        print()


if __name__ == '__main__':
    # 解析第一页.mhtml
    filepath = r'a:\建站\home\Home\第一页.mhtml'
    print('正在解析MHTML文件...\n')
    
    categories = parse_mhtml_file(filepath)
    
    print(f'找到 {len(categories)} 个分类\n')
    print('=' * 60)
    print('YAML格式输出：')
    print('=' * 60)
    print()
    
    output_yaml(categories)
    
    print('=' * 60)
    print(f'解析完成！共提取了 {len(categories)} 个分类')
    total_links = sum(len(cat['links']) for cat in categories)
    print(f'总计 {total_links} 个网站链接')
