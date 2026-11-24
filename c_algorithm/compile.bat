@echo off
echo ================================================================
echo   Compiling Intelligent Water Distribution System C Engine
echo ================================================================

REM Try GCC / Clang
where gcc >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set CC=gcc
    goto COMPILE
)

where clang >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set CC=clang
    goto COMPILE
)

echo No GCC or Clang found in system PATH.
exit /b 1

:COMPILE
echo Using C Compiler: %CC%

echo [1/2] Compiling Shared Dynamic Library (water_algorithm.dll)...
%CC% -O3 -shared -fPIC -o water_algorithm.dll water_distribution.c priority_queue.c graph.c linked_list.c -Wl,--out-implib,libwater_algorithm.a
if %ERRORLEVEL% neq 0 (
    echo Failed to build water_algorithm.dll
    exit /b 1
)
echo Successfully created water_algorithm.dll

echo [2/2] Compiling Standalone Console Demo (water_algorithm_demo.exe)...
%CC% -O3 -o water_algorithm_demo.exe main.c water_distribution.c priority_queue.c graph.c linked_list.c
if %ERRORLEVEL% neq 0 (
    echo Failed to build water_algorithm_demo.exe
    exit /b 1
)
echo Successfully created water_algorithm_demo.exe

echo All C components compiled successfully!
