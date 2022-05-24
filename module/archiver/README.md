# Thread Archive Module: thread-archive
## Mission Create
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "mission_create",
      "message_detail": {
        "mission_info": null
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
  "receiver": "thread-archive",
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

- Response
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

## Show Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "show_request",
      "message_detail": null
    }
  }
}
```

## Delete Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "delete_request",
      "message_detail": {
        "with_file": false
      }
    }
  }
}
```

## Archive Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "archive_request",
      "message_detail": {
        "download_info": null
      }
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
      "message_type": "archive_response",
      "message_detail": null
    }
  }
}
```

## Query Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "query_request",
      "message_detail": null
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
      "message_type": "query_response",
      "message_detail": {
        "mission_info": null,
        "download_info": null
      }
    }
  }
}
```

## Update Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
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

## State Request
- Request
```json
{
  "handle": "resend",
  "receiver": "thread-archive",
  "content": {
    "signal_type": "execute",
    "signal_detail": {
      "mission_uuid": "",
      "message_type": "state_request",
      "message_detail": {
        "mission_state": "sleeping|analyzing|running"
      }
    }
  }
}
```
