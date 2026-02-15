# 下载网站图标脚本
param(
    [string]$YamlFile = "exampleSite\data\webstack.yml",
    [string]$OutputDir = "static\assets\images\logos"
)

# 确保输出目录存在
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 读取 YAML 文件
$lines = Get-Content $YamlFile -Encoding UTF8
$newLines = @()

$downloaded = 0
$failed = 0
$currentTitle = ""
$currentUrl = ""

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # 检测 title
    if ($line -match '^\s+- title:\s+(.+)$') {
        $currentTitle = $matches[1].Trim()
    }
    # 检测 url  
    elseif ($line -match '^\s+url:\s+(https?://[^\s]+)') {
        $currentUrl = $matches[1].Trim()
    }
    # 检测并替换 logo
    elseif ($line -match '^(\s+logo:\s+)default\.webp$' -and $currentTitle -and $currentUrl) {
        Write-Host "处理: $currentTitle ($currentUrl)" -ForegroundColor Cyan
    
    try {
        # 从 URL 提取域名
        $uri = [System.Uri]$url
        $domain = $uri.Host -replace '^www\.', ''
        $filename = "$domain.png"
        $outputPath = Join-Path $OutputDir $filename
        
        # 如果文件已存在，跳过
        if (Test-Path $outputPath) {
            Write-Host "  图标已存在，跳过" -ForegroundColor Yellow
            continue
        }
        
        # 尝试多个可能的 favicon 位置
        $faviconUrls = @(
            "$($uri.Scheme)://$($uri.Host)/favicon.ico",
            "$($uri.Scheme)://$($uri.Host)/favicon.png",
            "$($uri.Scheme)://$($uri.Host)/apple-touch-icon.png",
            "https://www.google.com/s2/favicons?domain=$($uri.Host)&sz=128"
        )
        
        $success = $false
        foreach ($faviconUrl in $faviconUrls) {
            try {
                Invoke-WebRequest -Uri $faviconUrl -OutFile $outputPath -TimeoutSec 10 -ErrorAction Stop
                
                # 检查文件大小，如果太小可能是错误页面
                $fileInfo = Get-Item $outputPath
                if ($fileInfo.Length -gt 100) {
                    Write-Host "  ✓ 下载成功: $filename" -ForegroundColor Green
                    $downloaded++
                    $success = $true
                    
                    # 更新 YAML 文件中的图标路径
                    $content = $content -replace "(title:\s+$([regex]::Escape($title))\s+logo:\s+)default\.webp", "`$1$filename"
                    break
                }
            }
            catch {
                continue
            }
        }
        
        if (-not $success) {
            Write-Host "  ✗ 下载失败" -ForegroundColor Red
            $failed++
            if (Test-Path $outputPath) {
                Remove-Item $outputPath -Force
            }
        }
        
        Start-Sleep -Milliseconds 500  # 避免请求过快
    }
    catch {
        Write-Host "  ✗ 错误: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

# 保存更新后的 YAML 文件
$content | Out-File $YamlFile -Encoding UTF8

Write-Host "`n完成!" -ForegroundColor Green
Write-Host "成功下载: $downloaded" -ForegroundColor Green
Write-Host "失败: $failed" -ForegroundColor Yellow
