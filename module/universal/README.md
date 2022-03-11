# Thread Log Module: thread-log
## Console
- Request
```json
{
  "receiver": "thread-log",
  "value": {
    "mission_uuid": "",
    "message_type": "console",
    "detail": {
      "sender": "ClassName",
      "content": "str"
    }
  }
}
```

## File
- Request
```json
{
  "receiver": "thread-log",
  "value": {
    "mission_uuid": "",
    "message_type": "file",
    "detail": {
      "sender": "ClassName",
      "content": "str"
    }
  }
}
```

# Thread Open Module: thread-open
## Open
- Request
```json
{
  "receiver": "thread-open",
  "value": {
    "mission_uuid": "",
    "message_type": "open",
    "detail": {
      "path": "absolute_path"
    }
  }
}
```

# Thread Speed Module: thread-speed
## Register
- Request
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "register",
    "detail": {
      "download_info": null
    }
  }
}
```

## Change
- Request
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "change",
    "detail": {
      "size": 0
    }
  }
}
```

## Delete
- Request
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "delete",
    "detail": null
  }
}
```