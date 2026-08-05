#!/data/data/com.termux/files/usr/bin/bash

cd ~/STARCORE || exit 1

echo "Updating packages..."
pkg update -y
pkg upgrade -y

echo
echo "Cleaning Git..."

git gc
git prune

echo
echo "Refreshing GitHub authentication..."
gh auth status || gh auth refresh -h github.com

echo
echo "Repository verification..."

git fsck --full

echo
echo "Done."
