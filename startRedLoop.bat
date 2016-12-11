@Echo off
chcp 65001
:Start

python3 red.py
timeout 3

goto Start