#!/data/data/com.termux/files/usr/bin/bash

echo
echo "================================="
echo " STARCORE AI MODULE"
echo "================================="

echo
echo "Python:"
python --version

echo
echo "Virtual Environment:"
if [ -d "$HOME/STARCORE/.venv" ]; then
echo "OK .venv"
else
echo "Missing"
fi

echo
echo "AI directories:"

find "$HOME/STARCORE/ai" -maxdepth 1 -type d 2>/dev/null

