# Action Print
## normal
```json
{
  "action": "signal",
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

## exception
```json
{
  "action": "signal",
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
  "action": "signal",
  "receiver": "speed",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "schema": "",
      "download_info": {}
    }
  }
}
```

## Size
```json
{
  "action": "signal",
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
  "action": "signal",
  "receiver": "speed",
  "value": {
    "type": "finish",
    "mission_uuid": "",
    "detail": {}
  }
}
```

## Heart Beat
```json
{
  "action": "signal",
  "receiver": "speed",
  "value": {
    "type": "heartbeat",
    "mission_uuid": null,
    "detail": {}
  }
}
```

# Action Analyse
## request
```json
{
  "action": "signal",
  "receiver": "analyze",
  "value": {
    "type": "request",
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
  "action": "signal",
  "receiver": "write",
  "value": {
    "type": "register",
    "mission_uuid": "",
    "detail": {
      "save_path": "",
      "download_info": {}
    }
  }
}
```

## Write
```json
{
  "action": "signal",
  "receiver": "write",
  "value": {
    "type": "write",
    "mission_uuid": "",
    "detail": {
      "start_position": 0,
      "content": "bytes"
    }
  }
}
```

## Finish
```json
{
  "action": "signal",
  "receiver": "write",
  "value": {
    "type": "finish",
    "mission_uuid": "",
    "detail": {}
  }
}
```

# Action Open
## Open
```json
{
  "action": "signal",
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
