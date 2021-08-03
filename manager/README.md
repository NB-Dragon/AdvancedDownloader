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

## update_mission_config
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "update_mission_config",
    "mission_uuid": "",
    "detail": {
      "mission_info": {}
    }
  }
}
```

## update_download_name
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "update_download_name",
    "mission_uuid": "",
    "detail": {
      "sub_old_path": "",
      "sub_new_path": ""
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
    "detail": {
      "sub_path": ""
    }
  }
}
```

## request_info
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "request_info",
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

## update_section
```json
{
  "action": "signal",
  "receiver": "info",
  "value": {
    "type": "update_section",
    "mission_uuid": "",
    "detail": {
      "sub_path": "",
      "position": 0,
      "length": 0
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

# Action Thread
