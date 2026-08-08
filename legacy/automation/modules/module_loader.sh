#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/STARCORE"
MODULE_DIR="$ROOT/automation/modules"

load_module() {

MODULE="$1"

if [ -f "$MODULE_DIR/$MODULE.sh" ]; then
    bash "$MODULE_DIR/$MODULE.sh"
else
    echo "MODULE NOT FOUND: $MODULE"
fi

}
