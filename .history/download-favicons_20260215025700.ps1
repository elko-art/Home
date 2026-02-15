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
        Write-Host "处理: $currentTitle ($currentUrl)" -ForegroundColor Cyan
        
        try {
            # 从 URL 提取域名
            $uri = [System.Uri]$currentUrl
            $domain = $uri.Host -replace '^www\.', ''
            $filename = "$domain.png"
            $outputPath = Join-Path $OutputDir $filename
            
            # 如果文件已存在，直接使用
            if (Test-Path $outputPath) {
                Write-Host "  图标已存在: $filename" -ForegroundColor Yellow
                $newLines += $line -replace 'default\.webp', $filename
                $currentTitle = ""
                $currentUrl = ""
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
                    Invoke-WebRequest -Uri $faviconUrl -OutFile $outputPath -TimeoutSec 10 -ErrorAction Stop | Out-Null
                    
                    # 检查文件大小
                    $fileInfo = Get-Item $outputPath
                    if ($fileInfo.Length -gt 100) {
                        Write-Host "  下载成功: $filename" -ForegroundColor Green
                        $downloaded++
                        $success = $true
                        $newLines += $line -replace 'default\.webp', $filename
                        break
                    }
                }
                catch {
                    continue
                }
            }
            
            if (-not $success) {
                Write-Host "  下载失败，保持默认图标" -ForegroundColor Red
                $failed++
                if (Test-Path $outputPath) {
                    Remove-Item $outputPath -Force
                }
                $newLines += $line
            }
            
            Start-Sleep -Milliseconds 300
        }
        catch {
            Write-Host "  错误: $($_.Exception.Message)" -ForegroundColor Red
            $failed++
            $newLines += $line
        }
        
        $currentTitle = ""
        $currentUrl = ""
    }
    else {
        $newLines += $line
    }
}

# 保存更新后的 YAML 文件
$newLines | Out-File $YamlFile -Encoding UTF8

Write-Host "`n完成!" -ForegroundColor Green
Write-Host "成功下载: $downloaded" -ForegroundColor Green
Write-Host "失败: $failed" -ForegroundColor Yellow
