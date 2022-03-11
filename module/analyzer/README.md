# Thread Analyze Module: thread-analyze
## Analyze Request
- Request
```json
{
  "receiver": "thread-analyze",
  "value": {
    "mission_uuid": "",
    "message_type": "analyze_request",
    "detail": {
      "analyze_count": 0,
      "mission_info": null
    }
  }
}
```

- Response
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "analyze_response",
    "detail": {
      "analyze_count": 0,
      "mission_info": null,
      "download_info": null
    }
  }
}
```