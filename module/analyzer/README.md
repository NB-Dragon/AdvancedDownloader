# Thread Analyze Module: thread-analyze
## Analyze Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-analyze",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "analyze_request",
      "message_detail": {
        "analyze_count": 0,
        "mission_info": null
      }
    }
  }
}
```

- Response
```json
{
  "handle": "resend",
  "receiver": "thread-transform",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "analyze_response",
      "message_detail": {
        "analyze_count": 0,
        "mission_info": null,
        "download_info": null
      }
    }
  }
}
```