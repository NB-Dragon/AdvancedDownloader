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
  "action": "speed",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "register",
      "download_info": {}
    }
  }
}
```

## Size
```json
{
  "action": "speed",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "size",
      "length": 0
    }
  }
}
```

## Finish
```json
{
  "action": "speed",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "finish"
    }
  }
}
```

## Heart Beat
```json
{
  "action": "speed",
  "value": {
    "mission_uuid": null,
    "detail": {
      "type": "heartbeat"
    }
  }
}
```

# Action Write
## Register
```json
{
  "action": "write",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "register",
      "lock": "threading.Lock",
      "mission_info": {},
      "download_info": {}
    }
  }
}
```

## Write
```json
{
  "action": "write",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "write",
      "current_region": [],
      "content": "bytes"
    }
  }
}
```

## Split
```json
{
  "action": "write",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "split",
      "current_region": [],
      "update_region": [[]]
    }
  }
}
```

## Finish
```json
{
  "action": "write",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "finish"
    }
  }
}
```

# Action Open
## Open
```json
{
  "action": "open",
  "value": {
    "mission_uuid": "",
    "detail": {
      "type": "open",
      "path": ""
    }
  }
}
```
