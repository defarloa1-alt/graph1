#!/bin/bash

PIPELINE_STATUS=$1
BUILD_URL=$2
COMMIT_SHA=$3

if [ -z "$PIPELINE_STATUS" ]; then
    echo "Usage: $0 <status> [build_url] [commit_sha]"
    exit 1
fi

echo "Sending CI pipeline notification..."

# Determine status emoji and message
case $PIPELINE_STATUS in
    "success")
        EMOJI="SUCCESS"
        MESSAGE="CI Pipeline completed successfully!"
        COLOR="good"
        ;;
    "failure")
        EMOJI="FAILURE"
        MESSAGE="CI Pipeline failed!"
        COLOR="danger"
        ;;
    "warning")
        EMOJI="WARNING"
        MESSAGE="CI Pipeline completed with warnings!"
        COLOR="warning"
        ;;
    *)
        EMOJI="INFO"
        MESSAGE="CI Pipeline status: $PIPELINE_STATUS"
        COLOR="good"
        ;;
esac

# Send Slack notification if webhook is configured
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json'         --data "{
            "text": "$EMOJI $MESSAGE",
            "attachments": [
                {
                    "color": "$COLOR",
                    "fields": [
                        {
                            "title": "Build",
                            "value": "$BUILD_URL",
                            "short": true
                        },
                        {
                            "title": "Commit",
                            "value": "$COMMIT_SHA",
                            "short": true
                        }
                    ]
                }
            ]
        }"         $SLACK_WEBHOOK_URL
fi

echo "Notification sent: $MESSAGE"
