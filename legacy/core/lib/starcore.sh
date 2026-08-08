#!/data/data/com.termux/files/usr/bin/bash

STARCORE_ROOT="$HOME/STARCORE"

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

banner() {

echo
echo "========================================="
echo " STARCORE PLATFORM"
echo "========================================="
echo

}

info() {
echo -e "${BLUE}[INFO]${NC} $*"
}

ok() {
echo -e "${GREEN}[ OK ]${NC} $*"
}

warn() {
echo -e "${YELLOW}[WARN]${NC} $*"
}

fail() {
echo -e "${RED}[FAIL]${NC} $*"
}

timestamp() {
date "+%Y-%m-%d %H:%M:%S"
}

log() {

mkdir -p "$STARCORE_ROOT/logs/system"

echo "$(timestamp) $*" >> \
"$STARCORE_ROOT/logs/system/starcore.log"

}

run() {

CMD="$*"

info "$CMD"

eval "$CMD"

RET=$?

if [ "$RET" = 0 ]; then
    ok "$CMD"
else
    fail "$CMD"
fi

return "$RET"

}

require() {

if ! command -v "$1" >/dev/null
then
    fail "Missing command: $1"
    return 1
fi

}

save_json() {

FILE="$1"

shift

printf "%s\n" "$@" > "$FILE"

}

