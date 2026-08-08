#!/data/data/com.termux/files/usr/bin/bash

echo "===== SYSTEM ====="

uname -a

echo

echo "Android:"
getprop ro.product.model

echo

echo "Kernel:"
uname -r

