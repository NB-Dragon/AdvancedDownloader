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
## register
```json
{
  "action": "signal",
  "receiver": "mission_info",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "mission_info": {},
      "download_info": {}
    }
  }
}
```

## update
> The key in detail is optional
```json
{
  "action": "signal",
  "receiver": "mission_info",
  "value": {
    "type": "update",
    "mission_uuid": "",
    "detail": {
      "mission_info": {},
      "download_info": {}
    }
  }
}
```

## delete
```json
{
  "action": "signal",
  "receiver": "mission_info",
  "value": {
    "type": "delete",
    "mission_uuid": "",
    "detail": {
      "delete_file": false
    }
  }
}
```

## data
```json
{
  "action": "signal",
  "receiver": "mission_info",
  "value": {
    "type": "data",
    "mission_uuid": "",
    "detail": {}
  }
}
```

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
      "download_info": null
    }
  }
}
```
