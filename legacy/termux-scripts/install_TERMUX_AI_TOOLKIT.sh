#!/data/data/com.termux/files/usr/bin/bash


echo "=================================================="
echo " STARCORE TERMUX AI TOOLKIT"
echo "=================================================="


pkg install -y \
sqlite \
openssl \
libffi \
openssl-tool


pip install \
openai \
anthropic \
python-dotenv \
rich-click \
typer


npm install -g \
eslint \
prettier


mkdir -p ~/STARCORE/tools/ai


cat > ~/STARCORE/tools/ai/environment_check.sh <<'SH'

#!/data/data/com.termux/files/usr/bin/bash

echo "===== STARCORE AI ENV ====="

python --version

node --version

npm --version

claude --version

git status

SH


chmod +x ~/STARCORE/tools/ai/environment_check.sh


~/STARCORE/tools/ai/environment_check.sh


echo "=================================================="
echo " AI TOOLKIT READY"
echo "=================================================="


