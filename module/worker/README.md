# Thread Control Module: thread-control
## Data Sync
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-control",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "data_sync",
      "message_detail": {
        "mission_info": null
      }
    }
  }
}
```

## Data Response
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-control",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "data_response",
      "message_detail": {
        "download_info": null
      }
    }
  }
}
```

## Mission Start
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-control",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "mission_start",
      "message_detail": null
    }
  }
}
```

- Response Fail
```json
{
  "handle": "resend",
  "receiver": "thread-transform",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "data_request",
      "message_detail": null
    }
  }
}
```

## Mission Pause
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-control",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "mission_pause",
      "message_detail": null
    }
  }
}
```

## Mission Delete
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-control",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "mission_delete",
      "message_detail": {
        "delete_file": false
      }
    }
  }
}
```

## Process Update
- Request
```json
{
  "signal_type": "execute",
  "signal_detail": {
    "mission_uuid": "",
    "message_type": "process_update",
    "message_detail": {
      "section_uuid": "",
      "write_position": 0,
      "write_length": 0
    }
  }
}
```

- Response
```json
{
  "handle": "resend",
  "receiver": "thread-transform",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "update_request",
      "message_detail": {
        "section_uuid": "",
        "write_position": 0,
        "write_length": 0
      }
    }
  }
}
```

## Process Pause
- Request
```json
{
  "signal_type": "execute",
  "signal_detail": {
    "mission_uuid": "",
    "message_type": "process_pause",
    "message_detail": null
  }
}
```

## Process Finish
- Request
```json
{
  "signal_type": "execute",
  "signal_detail": {
    "mission_uuid": "",
    "message_type": "process_finish",
    "message_detail": {
      "delete_file": false
    }
  }
}
```

- Response
```json
{
  "handle": "resend",
  "receiver": "thread-transform",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "delete_request",
      "message_detail": {
        "delete_file": false
      }
    }
  }
}
```
