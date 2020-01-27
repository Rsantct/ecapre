#!/bin/bash

ecapreURL=http://localhost:8080


if [[ "$1" == "stop" || "$1" == "close" ]]; then
    osascript -e \
        "
        tell application \"Safari\"
            set winlist to count of every window
            repeat with wIdx from 1 to winlist
                close (every tab of window wIdx whose name = \"ecapre\")
            end repeat
        end tell
        "
    exit 0
fi

osascript -e \
    "
    tell application \"Safari\"
        make new document
        set URL of document 1 to \"${ecapreURL}\"
        tell window 1
            set bounds to {60, 60, 460, 400}
        end tell
    end tell
    "

exit 0

