#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "=================================================="
echo " TERMUX SAFE OPTIMIZER"
echo "=================================================="


mkdir -p \
~/workspace \
~/tools \
~/scripts \
~/logs



cat >> ~/.bashrc <<'BASH'

export STARCORE_HOME=$HOME/STARCORE

alias sc='cd $STARCORE_HOME'

alias scl='git log --oneline -10'

alias scs='git status'

alias ll='ls -lah'

BASH



apt clean || true


cat > "$BASE/runtime/termux/optimization.json" <<JSON
{
 "component":"STARCORE Termux Optimizer",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "changes":[
 "directories",
 "aliases",
 "cache_cleanup",
 "environment"
 ],
 "status":"complete"
}
JSON


cat "$BASE/runtime/termux/optimization.json"


echo "=================================================="


