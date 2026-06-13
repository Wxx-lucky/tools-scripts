@echo off
chcp 65001 >nul
title WenJian GeShi ZhuanHuan GongJu

set "PY=D:\mineru-env\Scripts\python.exe"
set "SC=%~dp0convert.py"

if not exist "%PY%" (
    echo [ERROR] Python not found: %PY%
    pause
    exit /b 1
)

if not exist "%SC%" (
    echo [ERROR] Script not found: %SC%
    pause
    exit /b 1
)

"%PY%" "%SC%" %1
pause
