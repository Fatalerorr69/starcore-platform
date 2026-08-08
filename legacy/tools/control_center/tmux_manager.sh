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

