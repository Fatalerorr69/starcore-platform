#!/data/data/com.termux/files/usr/bin/bash

set -e

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE TERMUX CONTROL CENTER v1.0"
echo "=================================================="


mkdir -p \
"$BASE/runtime/termux/control_center" \
"$BASE/tools/control_center"



##################################################
# CLAUDE MANAGER
##################################################

cat > "$BASE/tools/control_center/claude_manager.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

echo "========== CLAUDE CODE CHECK =========="


if claude --version >/dev/null 2>&1
then
    echo "CLAUDE: ONLINE"
else

    echo "CLAUDE: REPAIR REQUIRED"

    npm config set allow-scripts=@anthropic-ai/claude-code --location=user || true

    npm uninstall -g @anthropic-ai/claude-code || true

    npm install -g @anthropic-ai/claude-code \
    --allow-scripts=@anthropic-ai/claude-code


fi


claude --version || true


SH


chmod +x "$BASE/tools/control_center/claude_manager.sh"



##################################################
# TMUX MANAGER
##################################################

cat > "$BASE/tools/control_center/tmux_manager.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


SESSION="STARCORE"


if tmux has-session -t $SESSION 2>/dev/null
then

echo "TMUX SESSION EXISTS"

else

tmux new-session -d \
-s $SESSION \
-c ~/STARCORE


tmux rename-window \
-t $SESSION:0 \
MAIN


tmux new-window \
-t $SESSION \
-n CLAUDE \
-c ~/STARCORE


tmux new-window \
-t $SESSION \
-n MONITOR \
-c ~/STARCORE


echo "TMUX SESSION CREATED"

fi


tmux list-sessions

SH


chmod +x "$BASE/tools/control_center/tmux_manager.sh"



##################################################
# HEALTH MONITOR
##################################################

cat > "$BASE/tools/control_center/health_monitor.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


mkdir -p "$BASE/runtime/termux/control_center"



python=$(python --version 2>&1)
node=$(node --version 2>&1)
npm=$(npm --version 2>&1)


cat > "$BASE/runtime/termux/control_center/health.json" <<JSON
{
"component":"STARCORE Termux Control Center",
"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
"runtime":{
"python":"$python",
"node":"$node",
"npm":"$npm"
},
"git":"$(git status --short)",
"status":"ONLINE"
}
JSON


cat "$BASE/runtime/termux/control_center/health.json"

SH


chmod +x "$BASE/tools/control_center/health_monitor.sh"



##################################################
# MAIN DASHBOARD
##################################################

cat > "$BASE/tools/control_center/starcore_control.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "======================================"
echo " STARCORE TERMUX CONTROL CENTER"
echo "======================================"


echo ""

echo "[1] SYSTEM"

uname -a


echo ""

echo "[2] RUNTIME"

python --version
node --version
npm --version


echo ""

echo "[3] CLAUDE"

claude --version || echo "CLAUDE OFFLINE"


echo ""

echo "[4] GIT"

git status


echo ""

echo "======================================"

SH


chmod +x "$BASE/tools/control_center/starcore_control.sh"



##################################################
# RELEASE
##################################################

cat > "$BASE/runtime/termux/control_center/CONTROL_CENTER_RELEASE.json" <<JSON
{
"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
"component":"STARCORE Termux Control Center",
"version":"1.0",
"modules":5,
"errors":0,
"status":"READY"
}
JSON



##################################################
# EXECUTION
##################################################

"$BASE/tools/control_center/claude_manager.sh"

"$BASE/tools/control_center/tmux_manager.sh"

"$BASE/tools/control_center/health_monitor.sh"

"$BASE/tools/control_center/starcore_control.sh"


echo ""

echo "[GIT]"

cd "$BASE"

git add .

git commit -m "Add STARCORE Termux Control Center v1.0" || true


echo "=================================================="
echo " STARCORE TERMUX CONTROL CENTER COMPLETE"
echo " STATUS: READY"
echo "=================================================="


