#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "=========================================="
echo " STARCORE TERMUX CONTROL CENTER INSTALL"
echo "=========================================="

set -e


########################################
# DIRECTORIES
########################################

mkdir -p \
"$BASE/control_center/bin" \
"$BASE/control_center/modules" \
"$BASE/control_center/config" \
"$BASE/control_center/logs" \
"$BASE/control_center/state" \
"$BASE/control_center/backups"


########################################
# BACKUP
########################################

BACKUP="$BASE/control_center/backups/install_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP"

cp -r \
"$BASE/bin" \
"$BASE/control" \
"$BASE/config" \
"$BACKUP/" 2>/dev/null || true


########################################
# CONFIG
########################################

cat > "$BASE/control_center/config/control.json" <<EOF
{
 "name":"STARCORE Termux Control Center",
 "version":"1.0",
 "device":"Android Termux",
 "modules":[
   "system",
   "storage",
   "network",
   "git",
   "python",
   "node",
   "services",
   "security",
   "backup"
 ],
 "status":"ACTIVE"
}
EOF



########################################
# LOGGER
########################################

cat > "$BASE/control_center/bin/log.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash

LOG="$HOME/STARCORE/control_center/logs/control.log"

echo "$(date '+%F %T') | $*" >> "$LOG"

EOF



########################################
# SYSTEM MODULE
########################################


cat > "$BASE/control_center/modules/system.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "===== SYSTEM ====="

uname -a

echo

echo "Android:"
getprop ro.product.model

echo

echo "Kernel:"
uname -r

EOF



########################################
# STORAGE MODULE
########################################


cat > "$BASE/control_center/modules/storage.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "===== STORAGE ====="

df -h "$HOME"

echo

du -sh "$HOME/STARCORE"

EOF




########################################
# RUNTIME MODULE
########################################


cat > "$BASE/control_center/modules/runtime.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "===== RUNTIME ====="

python --version

node --version

npm --version

git --version

EOF




########################################
# NETWORK MODULE
########################################


cat > "$BASE/control_center/modules/network.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash


echo "===== NETWORK ====="


ip addr 2>/dev/null


echo

ping -c 2 8.8.8.8

EOF




########################################
# GIT MODULE
########################################


cat > "$BASE/control_center/modules/git.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "===== GIT ====="


git -C "$BASE" status

echo

git -C "$BASE" branch

EOF




########################################
# SECURITY MODULE
########################################


cat > "$BASE/control_center/modules/security.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash


echo "===== SECURITY ====="


echo "UID:"
id


echo

echo "Termux permissions:"


termux-info 2>/dev/null

EOF




########################################
# MAIN CONTROLLER
########################################


cat > "$BASE/control_center/bin/control-center" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE/control_center"


case "$1" in


system)

bash "$BASE/modules/system.sh"
;;


storage)

bash "$BASE/modules/storage.sh"
;;


runtime)

bash "$BASE/modules/runtime.sh"
;;


network)

bash "$BASE/modules/network.sh"
;;


git)

bash "$BASE/modules/git.sh"
;;


security)

bash "$BASE/modules/security.sh"
;;


health)

echo "===== CONTROL CENTER HEALTH ====="

for m in "$BASE"/modules/*.sh
do
 echo "[OK] $(basename $m)"
done

;;


all)

for m in "$BASE"/modules/*.sh
do
echo
bash "$m"
done

;;


*)

echo "
STARCORE CONTROL CENTER

Usage:

control-center system
control-center storage
control-center runtime
control-center network
control-center git
control-center security
control-center health
control-center all

"

;;

esac

EOF



chmod +x \
"$BASE/control_center/bin/"* \
"$BASE/control_center/modules/"*



########################################
# LINK COMMAND

########################################


ln -sf \
"$BASE/control_center/bin/control-center" \
"$BASE/bin/control-center"



echo
echo "================================="
echo " CONTROL CENTER INSTALLED"
echo "================================="

echo

echo "Command:"
echo

echo "control-center health"

