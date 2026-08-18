@echo off
set "FILE_PATH=%~dp0index.html"

:: Check for Microsoft Edge or Chrome to open in dedicated Web App Mode
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="file:///%FILE_PATH%"
    exit
)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="file:///%FILE_PATH%"
    exit
)

:: Fallback: Open in default web browser
start "" "%FILE_PATH%"