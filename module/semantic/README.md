# Thread Transform Module: thread-transform
## Create Command
- Request
```json
{
  "receiver": "thread-transform",
  "value": {
    "mission_uuid": "",
    "message_type": "create_command",
    "detail": {
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
    "message_type": "create_request",
    "detail": {
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
    "detail": null
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
    "detail": null
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
    "detail": null
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
    "detail": null
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
    "detail": {
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
    "detail": {
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
    "detail": null
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
    "detail": null
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
    "detail": {
      "update_size": 0,
      "download_info": null
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
    "message_type": "archive_request",
    "detail": {
      "download_info": null
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
    "detail": {
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
    "detail": {
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
    "detail": {
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
    "detail": null
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
    "detail": {
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
    "detail": {
      "mission_info": null,
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
    "detail": {
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
    "detail": {
      "success": true
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
    "message_type": "mission_start",
    "detail": null
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
    "detail": {
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
    "detail": {
      "analyze_count": 0,
      "mission_info": null
    }
  }
}
```

- Response Success
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "data_response",
    "detail": {
      "mission_info": null,
      "download_info": null
    }
  }
}
```