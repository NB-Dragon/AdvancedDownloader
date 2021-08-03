# Action Message
> The detail of value is refer to README.md in the listener directory.
```json
{
  "receiver": "parent.message.*",
  "value": {}
}
```

# Action Info
## Register
```json
{
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

## Update Mission Config
```json
{
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

## Update Download Name
```json
{
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

## Open
```json
{
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

## Request Info
```json
{
  "receiver": "info",
  "value": {
    "type": "request_info",
    "mission_uuid": "",
    "detail": null
  }
}
```

## Request Result
```json
{
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

## Update Section
```json
{
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

## Delete
```json
{
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
