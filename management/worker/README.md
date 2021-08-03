# Action Print
## Normal
```json
{
  "receiver": "print",
  "value": {
    "type": "normal",
    "mission_uuid": "",
    "detail": {
      "sender": "ClassName",
      "content": "str|dict"
    }
  }
}
```

## Exception
```json
{
  "receiver": "print",
  "value": {
    "type": "exception",
    "mission_uuid": "",
    "detail": {
      "sender": "ClassName",
      "content": "str|dict"
    }
  }
}
```

# Action Speed
## Register
```json
{
  "receiver": "speed",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "download_info": {}
    }
  }
}
```

## Size
```json
{
  "receiver": "speed",
  "value": {
    "type": "size",
    "mission_uuid": "",
    "detail": {
      "length": 0
    }
  }
}
```

## Finish
```json
{
  "receiver": "speed",
  "value": {
    "type": "finish",
    "mission_uuid": "",
    "detail": null
  }
}
```

## Heart Beat
```json
{
  "receiver": "speed",
  "value": {
    "type": "heartbeat",
    "mission_uuid": null,
    "detail": null
  }
}
```

# Action Analyze
## Request Info
```json
{
  "receiver": "analyze",
  "value": {
    "type": "request_info",
    "mission_uuid": "",
    "detail": {
      "schema": "",
      "analyze_tag": 0,
      "mission_info": {}
    }
  }
}
```

# Action Write
## Register
```json
{
  "receiver": "write",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "root_path": "",
      "download_info": {}
    }
  }
}
```

## Write
```json
{
  "receiver": "write",
  "value": {
    "type": "write",
    "mission_uuid": "",
    "detail": {
      "save_path": "",
      "start_position": 0,
      "content": "bytes"
    }
  }
}
```

## Finish
```json
{
  "receiver": "write",
  "value": {
    "type": "finish",
    "mission_uuid": "",
    "detail": {
      "delete_file": false
    }
  }
}
```

# Action Open
## Open
```json
{
  "receiver": "open",
  "value": {
    "type": "open",
    "mission_uuid": "",
    "detail": {
      "path": ""
    }
  }
}
```
