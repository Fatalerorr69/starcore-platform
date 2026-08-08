#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "=================================================="
echo " STARCORE CLAUDE RUNTIME REPAIR v1.0"
echo "=================================================="


mkdir -p \
"$BASE/runtime/termux/claude"



echo "[1] NODE ENV"

node --version

npm --version



echo "[2] GLOBAL MODULE LOCATION"


PREFIX=$(npm root -g)

echo "$PREFIX"


echo "[3] MODULE CHECK"


ls -la "$PREFIX/@anthropic-ai" || true



echo "[4] MANUAL POSTINSTALL"


CLAUDE_DIR="$PREFIX/@anthropic-ai/claude-code"


if [ -d "$CLAUDE_DIR" ]
then

cd "$CLAUDE_DIR"

node install.cjs || true

else

echo "CLAUDE PACKAGE NOT FOUND"

fi



echo "[5] REINSTALL CLEAN"


npm uninstall -g @anthropic-ai/claude-code || true


npm cache clean --force || true


npm install -g \
@anthropic-ai/claude-code \
--allow-scripts=@anthropic-ai/claude-code



echo "[6] VALIDATION"



CLAUDE_STATUS="offline"


if claude --version >/tmp/claude_test 2>&1
then

CLAUDE_STATUS="online"

cat /tmp/claude_test

else

cat /tmp/claude_test

fi



cat > "$BASE/runtime/termux/claude/claude_runtime.json" <<JSON
{
"component":"STARCORE Claude Runtime",
"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
"status":"$CLAUDE_STATUS",
"node":"$(node --version)",
"npm":"$(npm --version)"
}
JSON



cat "$BASE/runtime/termux/claude/claude_runtime.json"



echo "[GIT]"


cd "$BASE"

git add .

git commit -m "Add Claude Runtime Repair Layer" || true



echo "=================================================="
echo " CLAUDE REPAIR COMPLETE"
echo "=================================================="


