#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import quopri

def decode_quoted_printable(text):
    """解码quoted-printable编码的文本"""
    if '=' not in text:
        return text
    try:
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
    html_content = html_content.replace('=\n', '')  # 移除软换行
    
    # 确定当前激活的标签页
    active_tab_match = re.search(r'<li class="ta ua">([^<]+)</li>', html_content)
    if active_tab_match:
        active_tab = decode_quoted_printable(active_tab_match.group(1))
    else:
        active_tab = "未知"
    
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
    print("正在解析第二页...")
    page2_data = parse_mhtml_file(r'第二页.mhtml')
    
    print("正在解析第三页...")
    page3_data = parse_mhtml_file(r'第三页.mhtml')
    
    # 构建YAML结构
    yaml_lines = []
    
    # 处理第二页 (下载)
    if page2_data:
        yaml_lines.append("- taxonomy: 第二页")
        yaml_lines.append("  icon: fas fa-download fa-lg")
        yaml_lines.append("  list:")
        
        for category, links in page2_data['categories'].items():
            yaml_lines.append(f"  - term: {category}")
            yaml_lines.append("    links:")
            for link in links:
                yaml_lines.append(f"    - title: {link['title']}")
                yaml_lines.append(f"      logo: {link['logo']}")
                yaml_lines.append(f"      url: {link['url']}")
                yaml_lines.append(f"      description: {link['description']}")
    
    # 处理第三页 (资源)
    if page3_data:
        yaml_lines.append("- taxonomy: 第三页")
        yaml_lines.append("  icon: fas fa-folder-open fa-lg")
        yaml_lines.append("  list:")
        
        for category, links in page3_data['categories'].items():
            yaml_lines.append(f"  - term: {category}")
            yaml_lines.append("    links:")
            for link in links:
                yaml_lines.append(f"    - title: {link['title']}")
                yaml_lines.append(f"      logo: {link['logo']}")
                yaml_lines.append(f"      url: {link['url']}")
                yaml_lines.append(f"      description: {link['description']}")
    
    # 保存到文件
    yaml_content = '\n'.join(yaml_lines)
    with open(r'extracted_webstack.yml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print("\n提取完成！")
    print(f"第二页包含 {len(page2_data['categories']) if page2_data else 0} 个分类")
    print(f"第三页包含 {len(page3_data['categories']) if page3_data else 0} 个分类")
    print("\n已保存到: extracted_webstack.yml")
    
    # 输出第一个分类的统计
    if page2_data:
        print("\n第二页分类:")
        for cat in page2_data['categories'].keys():
            print(f"  - {cat} ({len(page2_data['categories'][cat])} 个链接)")
    if page3_data:
        print("\n第三页分类:")
        for cat in page3_data['categories'].keys():
            print(f"  - {cat} ({len(page3_data['categories'][cat])} 个链接)")

if __name__ == '__main__':
    main()
