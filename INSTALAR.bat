@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Instalando os sons do Claude Code ===
echo.
where py >nul 2>nul && (py -3 instalar.py %* & goto fim)
where python >nul 2>nul && (python instalar.py %* & goto fim)
echo ERRO: Python nao encontrado.
echo Instale o Python 3 em https://www.python.org/downloads/ (marque "Add python.exe to PATH")
echo e rode este arquivo de novo.
:fim
echo.
pause
