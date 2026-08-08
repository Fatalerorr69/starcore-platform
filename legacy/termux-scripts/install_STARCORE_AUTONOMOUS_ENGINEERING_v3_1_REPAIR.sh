#!/data/data/com.termux/files/usr/bin/bash

set -e

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE AUTONOMOUS ENGINEERING v3.1 REPAIR"
echo "=================================================="


mkdir -p \
"$BASE/tools/engineering" \
"$BASE/intelligence/reports" \
"$BASE/prompts/generated" \
"$BASE/runtime/engineering"


########################################
# REPOSITORY ANALYZER
########################################

cat > "$BASE/tools/engineering/analyze.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

REPORT="$BASE/intelligence/reports"

mkdir -p "$REPORT"


echo "STARCORE ANALYSIS"


find "$BASE" \
-type f \
-not -path "*/.git/*" \
> "$REPORT/files.txt"


find "$BASE" \
-name "*.py" \
> "$REPORT/python.txt"


find "$BASE" \
-name "*.js" \
-o -name "*.ts" \
> "$REPORT/javascript.txt"


find "$BASE" \
-name "Dockerfile*" \
-o -name "docker-compose*" \
> "$REPORT/docker.txt"


cat > "$REPORT/architecture_report.md" <<EOF

# STARCORE Architecture Report

Generated:
$(date)

Files:
$(wc -l < "$REPORT/files.txt")

Python:
$(wc -l < "$REPORT/python.txt")

Javascript:
$(wc -l < "$REPORT/javascript.txt")

Docker:
$(wc -l < "$REPORT/docker.txt")

