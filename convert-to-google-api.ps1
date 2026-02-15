# 将webstack.yml中的logo字段批量替换为Google Favicon API链接
# 确保图标尺寸统一

param(
    [string]$YamlFile = "exampleSite\data\webstack.yml",
    [int]$Size = 64  # 图标尺寸：16, 32, 64, 128, 256
)

Write-Host "正在处理 $YamlFile ..." -ForegroundColor Cyan
Write-Host "目标图标尺寸: ${Size}x${Size}px`n" -ForegroundColor Cyan

# 读取YAML文件
$content = Get-Content $YamlFile -Encoding UTF8 -Raw

# 统计信息
$totalConverted = 0
$errors = @()

# 正则模式：匹配 title, logo, url 三行组合
$pattern = '(?m)^(\s+- title: )(.+)\r?\n(\s+logo: )(.+)\r?\n(\s+url: )(https?://[^\r\n]+)'

$newContent = [regex]::Replace($content, $pattern, {
    param($match)
    
    $indent1 = $match.Groups[1].Value
    $title = $match.Groups[2].Value
    $indent2 = $match.Groups[3].Value
    $currentLogo = $match.Groups[4].Value
    $indent3 = $match.Groups[5].Value
    $url = $match.Groups[6].Value
    
    try {
        # 从URL提取域名
        $uri = [System.Uri]$url
        $domain = $uri.Host -replace '^www\.', ''
        
        # 构建Google Favicon API URL
        $newLogo = "https://www.google.com/s2/favicons?domain=$domain&sz=$Size"
        
        $script:totalConverted++
        Write-Host "  [$script:totalConverted] $title" -ForegroundColor Green
        Write-Host "      域名: $domain" -ForegroundColor Gray
        Write-Host "      API: $newLogo" -ForegroundColor Gray
        
        # 返回替换后的内容
        return "$indent1$title`n$indent2$newLogo`n$indent3$url"
    }
    catch {
        $script:errors += "处理失败: $title - $($_.Exception.Message)"
        Write-Host "  [✗] $title - 错误: $($_.Exception.Message)" -ForegroundColor Red
        # 保持原样
        return $match.Value
    }
})

# 保存文件
$newContent | Out-File $YamlFile -Encoding UTF8 -NoNewline

Write-Host "`n处理完成！" -ForegroundColor Green
Write-Host "成功转换: $totalConverted 个网站图标" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host "`n发现 $($errors.Count) 个错误：" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

Write-Host "`n所有图标已统一为 ${Size}x${Size}px 的Google API链接" -ForegroundColor Cyan
Write-Host "图标将在网站加载时自动从Google服务器获取" -ForegroundColor Cyan
