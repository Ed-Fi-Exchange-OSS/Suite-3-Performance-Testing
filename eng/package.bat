@echo off

choco install octopustools
call RefreshEnv.cmd

powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\package.ps1' %*;"
