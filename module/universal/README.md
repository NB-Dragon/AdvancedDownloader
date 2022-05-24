# Thread Interact Module: thread-interact
## Normal
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-interact",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "message_type": "normal",
      "message_detail": {
        "content": ""
      }
    }
  }
}
```

## Table
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-interact",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "message_type": "table",
      "message_detail": {
        "rows": [[], [], []]
      }
    }
  }
}
```

# Thread Log Module: thread-log
## Console
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-log",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "console",
      "message_detail": {
        "sender": "ClassName",
        "content": "str"
      }
    }
  }
}
```

## File
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-log",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "file",
      "message_detail": {
        "sender": "ClassName",
        "content": "str"
      }
    }
  }
}
```

# Thread Open Module: thread-open
## Open
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-open",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "open",
      "message_detail": {
        "path": "absolute_path"
      }
    }
  }
}
```

# Thread Speed Module: thread-speed
## Register
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-speed",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "register",
      "message_detail": {
        "download_info": null
      }
    }
  }
}
```

## Change
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-speed",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "change",
      "message_detail": {
        "size": 0
      }
    }
  }
}
```

## Delete
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-speed",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "delete",
      "message_detail": null
    }
  }
}
```
