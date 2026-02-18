@echo off
chcp 65001 >nul
echo 正在启动 Hugo 服务器...
cd /d "%~dp0exampleSite"
start http://localhost:1313/Home/
hugo server -D
