@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Removendo os sons do Claude Code ===
echo.
where py >nul 2>nul && (py -3 instalar.py --remover & goto fim)
where python >nul 2>nul && (python instalar.py --remover & goto fim)
echo ERRO: Python nao encontrado.
:fim
echo.
pause
