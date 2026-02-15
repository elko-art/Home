#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import quopri
from html.parser import HTMLParser
import yaml
from collections import OrderedDict

class MHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tab = None
        self.current_category = None
        self.in_category = False
        self.in_link = False
        self.current_link_data = {}
        self.data = {}
        self.tabs = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # 检测标签页
        if tag == 'li' and 'class' in attrs_dict:
            classes = attrs_dict['class'].split()
            if 'ta' in classes:
                # 我们需要在handle_data中获取文本
                self.in_tab = True
        
        # 检测分类标题
        if tag == 'span' and 'class' in attrs_dict and 'za' in attrs_dict['class'].split():
            self.in_category = True
            
        # 检测链接
        if tag == 'a' and 'class' in attrs_dict and 'Da' in attrs_dict['class'].split():
            self.in_link = True
            self.current_link_data = {
                'url': attrs_dict.get('href', ''),
                'title': '',
                'logo': 'default.webp'
            }
            
        # 检测链接文本
        if tag == 'span' and 'class' in attrs_dict and 'Ia' in attrs_dict['class'].split():
            self.in_link_text = True
            
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
            
        # 获取标签页名称
        if hasattr(self, 'in_tab') and self.in_tab:
            decoded = decode_quoted_printable(data)
            if decoded and decoded not in self.tabs:
                self.tabs.append(decoded)
            self.in_tab = False
            
        # 获取分类名称
        if self.in_category:
            decoded = decode_quoted_printable(data)
            if decoded:
                self.current_category = decoded
                if self.current_tab and self.current_tab not in self.data:
                    self.data[self.current_tab] = {}
                if self.current_tab and self.current_category not in self.data[self.current_tab]:
                    self.data[self.current_tab][self.current_category] = []
            self.in_category = False
            
        # 获取链接标题
        if hasattr(self, 'in_link_text') and self.in_link_text:
            decoded = decode_quoted_printable(data)
            if decoded and self.current_link_data:
                self.current_link_data['title'] = decoded
            self.in_link_text = False
            
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            if self.current_link_data and self.current_link_data.get('title'):
                if self.current_tab and self.current_category:
                    if self.current_tab not in self.data:
                        self.data[self.current_tab] = {}
                    if self.current_category not in self.data[self.current_tab]:
                        self.data[self.current_tab][self.current_category] = []
                    self.data[self.current_tab][self.current_category].append({
                        'title': self.current_link_data['title'],
                        'logo': 'default.webp',
                        'url': self.current_link_data['url'],
                        'description': self.current_link_data['title']
                    })
            self.in_link = False
            self.current_link_data = {}

def decode_quoted_printable(text):
    """解码quoted-printable编码的文本"""
    if '=' not in text:
        return text
    try:
        # 尝试解码
        decoded_bytes = quopri.decodestring(text.encode('ascii'))
        return decoded_bytes.decode('utf-8')
    except:
        return text

def parse_mhtml_file(filepath):
    """解析MHTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取HTML部分
    html_match = re.search(r'Content-Type: text/html.*?Content-Location:.*?\n\n(.*?)------MultipartBoundary', 
                          content, re.DOTALL)
    if not html_match:
        return None
        
    html_content = html_match.group(1)
    
    # 解析quoted-printable编码
    html_content = html_content.replace('=\n', '')  # 移除软换行
    
    # 查找所有标签页
    tab_pattern = r'<li class="ta[^"]*">([^<]+)</li>'
    tabs = re.findall(tab_pattern, html_content)
    
    # 解码标签页名称
    decoded_tabs = []
    for tab in tabs:
        decoded = decode_quoted_printable(tab)
        decoded_tabs.append(decoded)
    
    # 确定当前激活的标签页
    active_tab_match = re.search(r'<li class="ta ua">([^<]+)</li>', html_content)
    if active_tab_match:
        active_tab = decode_quoted_printable(active_tab_match.group(1))
    else:
        active_tab = decoded_tabs[0] if decoded_tabs else None
    
    # 提取所有分类和链接
    result = {}
    
    # 查找所有分类块
    category_pattern = r'<div class="wa">.*?<span class="za">([^<]+)</span>.*?<ul class="Aa">(.*?)</ul>'
    categories = re.findall(category_pattern, html_content, re.DOTALL)
    
    for cat_name_encoded, links_html in categories:
        cat_name = decode_quoted_printable(cat_name_encoded)
        
        # 提取该分类下的所有链接
        link_pattern = r'<a class="Da" href="([^"]+)"[^>]*>.*?<span class="Ia">([^<]+)</span>'
        links = re.findall(link_pattern, links_html, re.DOTALL)
        
        link_list = []
        for url, title_encoded in links:
            title = decode_quoted_printable(title_encoded)
            link_list.append({
                'title': title,
                'logo': 'default.webp',
                'url': url,
                'description': title
            })
        
        if link_list:
            result[cat_name] = link_list
    
    return {
        'tab': active_tab,
        'categories': result
    }

def main():
    # 解析两个MHTML文件
    page2_data = parse_mhtml_file(r'a:\建站\home\Home\第二页.mhtml')
    page3_data = parse_mhtml_file(r'a:\建站\home\Home\第三页.mhtml')
    
    # 构建YAML结构
    yaml_data = []
    
    # 处理第二页 (下载)
    if page2_data:
        page2_entry = {
            'taxonomy': '第二页',
            'icon': 'fas fa-download fa-lg',
            'list': []
        }
        
        for category, links in page2_data['categories'].items():
            page2_entry['list'].append({
                'term': category,
                'links': links
            })
        
        yaml_data.append(page2_entry)
    
    # 处理第三页 (资源)
    if page3_data:
        page3_entry = {
            'taxonomy': '第三页',
            'icon': 'fas fa-folder-open fa-lg',
            'list': []
        }
        
        for category, links in page3_data['categories'].items():
            page3_entry['list'].append({
                'term': category,
                'links': links
            })
        
        yaml_data.append(page3_entry)
    
    # 自定义YAML表示器以保持顺序
    def represent_ordereddict(dumper, data):
        return dumper.represent_dict(data.items())
    
    yaml.add_representer(OrderedDict, represent_ordereddict)
    
    # 输出YAML
    yaml_output = yaml.dump(yaml_data, 
                           allow_unicode=True, 
                           default_flow_style=False,
                           sort_keys=False,
                           indent=2)
    
    # 保存到文件
    with open(r'a:\建站\home\Home\extracted_webstack.yml', 'w', encoding='utf-8') as f:
        f.write(yaml_output)
    
    print("提取完成！")
    print(f"\n第二页包含 {len(page2_data['categories']) if page2_data else 0} 个分类")
    print(f"第三页包含 {len(page3_data['categories']) if page3_data else 0} 个分类")
    print("\n已保存到: a:\\建站\\home\\Home\\extracted_webstack.yml")

if __name__ == '__main__':
    main()
