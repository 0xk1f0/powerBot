#!/bin/bash

# initiation time
INIT_HR=$(date +%H)

# assume non run
IS_RUNNING=false

# if we find process
if pgrep -x runbot.py >> /dev/null; then
    # assume running
    IS_RUNNING=true;
else
    echo "The bot is NOT running!"
    # no run
    IS_RUNNING=false;
fi

# check for daily
if [ "$1" == "daily" ]; then
    # if bot is not running
    if $IS_RUNNING; then
        echo "Killing.."
        killall runbot.py
    fi
    echo "Starting with 'daily'.."
    ./runbot.py daily &
    disown
# else start normally
else
    if $IS_RUNNING; then
        echo "The bot is running!"
        echo "Not doing anything!"
    else
        echo "Starting.."
        ./runbot.py &
        disown
    fi
fi
