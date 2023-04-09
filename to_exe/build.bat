@echo off

set "{{=setlocal enableDelayedExpansion&for %%a in (" & set "}}="::end::" ) do if "%%~a" neq "::end::" (set command=!command! %%a) else (call !command! & endlocal)"

%{{%
    c: <PATH_TO_PY_ARMOR> pack
    -x " --advanced 2 --bootstrap 2 --enable-suffix"
    -e "
        -c
        --onefile
        --hidden-import pure-python-adb
        --hidden-import undetected_chromedriver
        --hidden-import smsactivate
        --hidden-import pandas
        --hidden-import urllib3
    "
    --name naos_gen
    gmail_gen.py
%}}%