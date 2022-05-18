# Thread Transform Module: thread-transform
## Create Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "create_command",
    "message_detail": {
      "mission_info": null
    }
  }
}
```

- Response
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "mission_create",
    "message_detail": {
      "mission_info": null
    }
  }
}
```

## Start Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "start_command",
    "message_detail": null
  }
}
```

- Response
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "mission_start",
    "message_detail": null
  }
}
```

## Show Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "show_command",
    "message_detail": null
  }
}
```

- Response
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "show_request",
    "message_detail": null
  }
}
```

## Pause Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "pause_command",
    "message_detail": null
  }
}
```

- Response
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "mission_pause",
    "message_detail": null
  }
}
```

## Delete Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "delete_command",
    "message_detail": {
      "delete_file": false
    }
  }
}
```

- Response
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "mission_delete",
    "message_detail": {
      "delete_file": false
    }
  }
}
```

## Data Request
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "data_request",
    "message_detail": null
  }
}
```

- Response
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "query_request",
    "message_detail": null
  }
}
```

## Update Request
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "update_request",
    "message_detail": {
      "section_uuid": "",
      "write_position": 0,
      "write_length": 0
    }
  }
}
```

- Response: Archive
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "update_request",
    "message_detail": {
      "section_uuid": "",
      "write_position": 0,
      "write_length": 0
    }
  }
}
```

- Response: Speed
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "change",
    "message_detail": {
      "size": 0
    }
  }
}
```

## Delete Request
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "delete_request",
    "message_detail": {
      "delete_file": false
    }
  }
}
```

- Response: Archive
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "delete_request",
    "message_detail": {
      "delete_file": false
    }
  }
}
```

- Response: Speed
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "delete",
    "message_detail": null
  }
}
```

## Analyze Response
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "analyze_response",
    "message_detail": {
      "analyze_count": 0,
      "mission_info": null,
      "download_info": null
    }
  }
}
```

- Response Fail
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "data_response",
    "message_detail": {
      "download_info": null
    }
  }
}
```

- Response Success
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "archive_request",
    "message_detail": {
      "download_info": null
    }
  }
}
```

## Archive Response
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "archive_response",
    "message_detail": null
  }
}
```

- Response
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "mission_start",
    "message_detail": null
  }
}
```

## Query Response
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "query_response",
    "message_detail": {
      "mission_info": null,
      "download_info": null
    }
  }
}
```

- Response Fail
```json
{
  "receiver": "thread-analyze",
  "value": {
    "mission_uuid": "",
    "message_type": "analyze_request",
    "message_detail": {
      "analyze_count": 0,
      "mission_info": null
    }
  }
}
```

- Response Success: Control
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "data_response",
    "message_detail": {
      "download_info": null
    }
  }
}
```

- Response Success: Speed
```json
{
  "receiver": "thread-speed",
  "value": {
    "mission_uuid": "",
    "message_type": "register",
    "message_detail": {
      "download_info": null
    }
  }
}
```