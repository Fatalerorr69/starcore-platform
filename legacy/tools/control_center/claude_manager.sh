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


