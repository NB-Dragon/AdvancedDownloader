# Action Message
> The detail of value is refer to README.md in the listener directory.
```json
{
  "action": "signal",
  "receiver": "message.*",
  "value": {}
}
```

# Action Info
## register
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "schema": "",
      "mission_info": {},
      "download_info": null
    }
  }
}
```

## update
> The key in detail is optional
```json
{
  "action": "signal",
  "receiver": "info",
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
  "receiver": "info",
  "value": {
    "type": "delete",
    "mission_uuid": "",
    "detail": {
      "delete_file": false
    }
  }
}
```

## open
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "open",
    "mission_uuid": "",
    "detail": null
  }
}
```

## data
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "data",
    "mission_uuid": "",
    "detail": null
  }
}
```

## request_result
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "request_result",
    "mission_uuid": "",
    "detail": {
      "analyze_tag": 0,
      "download_info": null
    }
  }
}
```

# Action Thread
## write_done
```json
{
  "action": "signal",
  "receiver": "thread",
  "value": {
    "type": "write_done",
    "mission_uuid": "",
    "detail": {
      "start_position": 0,
      "length": 0
    }
  }
}
```