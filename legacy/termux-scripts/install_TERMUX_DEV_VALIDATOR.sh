#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


mkdir -p "$BASE/runtime/termux"


check(){

command -v "$1" >/dev/null \
&& echo "$1 : OK" \
|| echo "$1 : MISSING"

}


echo "=================================================="
echo " DEVELOPMENT STACK"
echo "=================================================="


for TOOL in \
git \
python \
node \
npm \
clang \
rustc \
cargo \
go \
tmux \
ssh
do

check $TOOL

done


cat > "$BASE/runtime/termux/dev_stack.json" <<JSON
{
"component":"STARCORE Termux Development Stack",
"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
"status":"checked"
}
JSON


cat "$BASE/runtime/termux/dev_stack.json"


