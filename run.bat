@echo off
REM ============================================================
REM  Predikcija potraznje i optimizacija zaliha
REM  Pokretanje Streamlit dashboarda jednim klikom
REM ============================================================
setlocal

REM Predji u folder u kojem se nalazi ovaj .bat (radi i ako se klikne sa desktopa)
cd /d "%~dp0"

set "VENV_PY=%~dp0venv\Scripts\python.exe"

echo.
echo  ============================================================
echo   Pokrecem dashboard: Predikcija potraznje i optimizacija zaliha
echo  ============================================================
echo.

if exist "%VENV_PY%" (
    echo  [OK] Koristim virtualno okruzenje ^(venv^).
    "%VENV_PY%" -m streamlit run app.py --server.port 8501
) else (
    echo  [!] venv nije pronadjen - koristim globalni Python.
    python -m streamlit run app.py --server.port 8501
)

REM Ako Streamlit padne, prozor ostaje otvoren da se vidi greska
if errorlevel 1 (
    echo.
    echo  [GRESKA] Aplikacija se nije pokrenula. Provjeri poruku iznad.
    echo.
    pause
)

endlocal
