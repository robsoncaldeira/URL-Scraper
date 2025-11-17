@echo off
REM Script para executar o URL Scraper com urls.txt e keywords.txt (Windows batch)
REM Uso: run_scraper.bat [mode] [follow_depth] [delay]
REM Exemplos:
REM   run_scraper.bat seed
REM   run_scraper.bat hybrid 1 2.0
REM   run_scraper.bat keywords

setlocal enabledelayedexpansion

REM Parâmetros padrão
set MODE=%1
if "%MODE%"=="" set MODE=seed

set FOLLOW_DEPTH=%2
if "%FOLLOW_DEPTH%"=="" set FOLLOW_DEPTH=0

set DELAY=%3
if "%DELAY%"=="" set DELAY=1.0

set URLS_FILE=urls.txt
set KEYWORDS_FILE=keywords.txt

REM Criar diretório de resultados se não existir
if not exist "results" mkdir results

REM Gerar timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

set OUTPUT_FILE=results\scraping_results_%TIMESTAMP%.json

echo.
echo URL Scraper - Modo: %MODE%
echo URLs file: %URLS_FILE%
echo Keywords file: %KEYWORDS_FILE%
echo Output: %OUTPUT_FILE%
echo Follow depth: %FOLLOW_DEPTH%
echo Delay: %DELAY% segundos
echo.

REM Construir e executar comando
python cli.py --mode %MODE% --delay %DELAY% --output "%OUTPUT_FILE%" ^
  --urls "%URLS_FILE%" --keywords "%KEYWORDS_FILE%" --follow-depth %FOLLOW_DEPTH%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Scraping concluido com sucesso!
    echo Resultados salvos em: %OUTPUT_FILE%
) else (
    echo.
    echo Erro ao executar CLI
    exit /b 1
)
