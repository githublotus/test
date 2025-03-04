#!/bin/sh

while true; do
    # Read all required variables at once
    SCAN_TIME=$(awk '/DAILY_SCAN_TIME_24H_IN_HOUR/ {print $3}' rcb.conf)
    EXPIRE_DATE=$(awk '/RECYCLE_BIN_EXPIRE_YYYYMMDD/ {print $3}' rcb.conf | tr -d '"')
    RECYCLE_BIN_ROOT_DIR=$(awk '/RECYCLE_BIN_ROOT_DIR/ {print $3}' rcb.conf | tr -d '"')

    # Get current date and time
    CURRENT_DATE=$(date +%Y-%m-%d)
    CURRENT_HOUR=$(date +%H)

    # echo "Current date: $CURRENT_DATE"
    # echo "Expire date: $EXPIRE_DATE"
    # echo "Scan time: $SCAN_TIME"

    # Check and run maintenance
    if [ "$CURRENT_DATE" \< "$EXPIRE_DATE" ] || [ "$CURRENT_DATE" = "$EXPIRE_DATE" ]; then
        if [ "$CURRENT_HOUR" = "$SCAN_TIME" ]; then
            START_TIME=$(date +%s)
            python rcb daily_maintenance
            echo $CURRENT_DATE >> rcb_daily_scan.log
            END_TIME=$(date +%s)

            # Calculate delay time = 24h - maintenance execution time
            EXEC_TIME=$((END_TIME - START_TIME))
            DELAY_TIME=$((86400 - EXEC_TIME - 1))

            echo "Maintenance execution time: $EXEC_TIME seconds"
            echo "Delay time until next run: $DELAY_TIME seconds"

            sleep $DELAY_TIME # Delay the remaining time to run next time (Exactly 24h)
        else
            # Delay 1 second to calibrate time before checking again
            sleep 1
        fi
    else
        # Clean up all data in recycle bin directory before exit
        echo "Recycle bin expired. Cleaning up all data then exiting..."
        rm -rdf "${RECYCLE_BIN_ROOT_DIR:?}"/*
        break # Exit loop if expiration date has passed
    fi
done
