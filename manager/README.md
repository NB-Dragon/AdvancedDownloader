# Action Message
> The detail of value is refer to README.md in the listener directory.
```json
{
  "action": "signal",
  "receiver": "message",
  "value": {}
}
```

# Action Analyse
## request
```json
{
  "action": "signal",
  "receiver": "analyse",
  "value": {
    "type": "request",
    "mission_uuid": "",
    "detail": {
      "analyse_tag": 0,
      "mission_info": {}
    }
  }
}
```

# Action Mission Info
## request_result
```json
{
  "action": "signal",
  "receiver": "mission_info",
  "value": {
    "type": "request_result",
    "mission_uuid": "",
    "detail": {
      "analyse_tag": 0,
      "download_info": {}
    }
  }
}
```
