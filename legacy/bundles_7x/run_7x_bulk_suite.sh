#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$HOME/STARCORE/bundles_7x"
./install_7_3_4_ai_infra_knowledge.sh
./install_7_5_6_studio_devops.sh
./install_7_7_8_marketplace_observability.sh
./install_7_9_10_security_final.sh
echo "=================================================="
echo " STARCORE 7.3-7.10 BULK SUITE COMPLETE"
echo "=================================================="
