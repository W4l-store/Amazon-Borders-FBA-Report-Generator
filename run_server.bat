@echo off

start cmd /k "python -m http.server 8002"

echo Press any key to start the server or close the window to stop...
pause >nul

start cmd /k "ngrok http --region=us --hostname=eminently-noted-rodent.ngrok-free.app 8002"

echo Server is running. Run macros in google docs and after Press any key to stop...
pause >nul

taskkill /IM ngrok.exe /F
taskkill /IM python.exe /F