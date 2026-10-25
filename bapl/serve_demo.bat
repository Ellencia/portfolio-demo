@echo off
rem Demo buyflow server on 127.0.0.1:8100 with the fake DB from seed_demo.py.
rem Every data/outside folder points at this demo folder so no real file names can show up.
set D=%~dp0
set BUYFLOW_DATA=%D%data
set BUYFLOW_DB=%D%data\buyflow.db
set BUYFLOW_SKIP_AUTH=1
set BUYFLOW_WORK_INBOX=%D%empty
set BUYFLOW_Z_ROOT=%D%empty
set BUYFLOW_INBOX=%D%empty
if not exist "%D%empty" mkdir "%D%empty"
cd /d "%D%..\..\..\projects\buyflow"
.venv\Scripts\python.exe -X utf8 -m buyflow serve --db "%BUYFLOW_DB%" --host 127.0.0.1 --port 8100
