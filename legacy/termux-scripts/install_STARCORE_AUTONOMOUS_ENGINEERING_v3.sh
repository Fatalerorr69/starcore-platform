#!/data/data/com.termux/files/usr/bin/bash

set -e

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE AUTONOMOUS ENGINEERING LAYER v3.0"
echo "=================================================="


mkdir -p \
$BASE/intelligence/reports \
$BASE/intelligence/scanners \
$BASE/sessions \
$BASE/prompts/generated \
$BASE/runtime/engineering \
$BASE/tools/engineering



############################################
# REPOSITORY ANALYZER
############################################


cat > $BASE/tools/engineering/analyze.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"

REPORT="$BASE/intelligence/reports"


mkdir -p "$REPORT"


echo "Generating STARCORE analysis..."



find "$BASE" \
-type f \
-not -path "*/.git/*" \
> "$REPORT/files.txt"



find "$BASE" \
-name "*.py" \
> "$REPORT/python_projects.txt"



find "$BASE" \
-name "*.js" \
-o -name "*.ts" \
> "$REPORT/node_projects.txt"



find "$BASE" \
-name "docker-compose*" \
-o -name "Dockerfile*" \
> "$REPORT/docker_inventory.txt"



grep -R \
-E "TODO|FIXME|BUG|HACK" \
"$BASE" \
--exclude-dir=.git \
> "$REPORT/issues.txt" \
|| true



cat > "$REPORT/architecture_report.md" <<EOF2
# STARCORE Architecture Report


Generated:
$(date)


## Statistics


Files:
$(wc -l < "$REPORT/files.txt")


Python:
$(wc -l < "$REPORT/python_projects.txt")


Node:
$(wc -l < "$REPORT/node_projects.txt")


Docker:
$(wc -l < "$REPORT/docker_inventory.txt")


Issues:
$(wc -l < "$REPORT/issues.txt")


EOF2


echo "REPORT READY"

SH


chmod +x $BASE/tools/engineering/analyze.sh



############################################
# PROMPT ENGINE
############################################


cat > $BASE/tools/engineering/prompt.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"

TYPE=$1


OUT="$BASE/prompts/generated"


mkdir -p "$OUT"



case "$TYPE" in


audit)

cat > "$OUT/audit_prompt.md" <<EOF

# STARCORE FULL AUDIT PROMPT


Analyze the STARCORE repository.


Context:

$(cat $BASE/config/ai_context.yaml)


Tasks:

1. Analyze architecture
2. Identify duplicate systems
3. Find unfinished modules
4. Create completion roadmap
5. Suggest refactoring


Do not modify files.

