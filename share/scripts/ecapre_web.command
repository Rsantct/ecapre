#!/bin/bash

URL=http://localhost:8080

osascript -e \
    "
    tell application \"Safari\"
        make new document
        set URL of document 1 to \"${URL}\"
        tell window 1
            set bounds to {60, 60, 460, 400}
        end tell
    end tell
    "

exit 0

