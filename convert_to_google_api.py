# 快速转换webstack.yml中的logo为Google API链接
import re
from urllib.parse import urlparse

yaml_file = r"exampleSite\data\webstack.yml"

with open(yaml_file, 'r', encoding='utf-8') as f:
    content = f.read()

def replace_logo(match):
    indent1 = match.group(1)
    title = match.group(2)
    indent2 = match.group(3)
    current_logo = match.group(4)
    indent3 = match.group(5)
    url = match.group(6)
    
    try:
        # 提取域名
        parsed = urlparse(url)
        domain = parsed.hostname.replace('www.', '') if parsed.hostname else url
        
        # 构建Google API URL
        new_logo = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        
        print(f"✓ {title}: {domain}")
        return f"{indent1}{title}\n{indent2}{new_logo}\n{indent3}{url}"
    except Exception as e:
        print(f"✗ {title}: Error - {e}")
        return match.group(0)

# 正则匹配：title, logo, url三行组合
pattern = r'^(\s+- title: )(.+)\n(\s+logo: )(.+)\n(\s+url: )(https?://[^\n]+)'

new_content = re.sub(pattern, replace_logo, content, flags=re.MULTILINE)

# 保存文件
with open(yaml_file, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print("\n✓ 转换完成！所有图标已替换为Google API链接（64x64px）")
