# Thread Control Module: thread-control
## Data Sync
- Request
```json
{
  "receiver": "thread-control",
  "value": {
    "mission_uuid": "",
    "message_type": "data_sync",
    "message_detail": {
      "mission_info": null,
      "download_info": null
    }
  }
}
```

## Data Response
- Request
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

## Mission Start
- Request
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

- Response Fail
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

## Mission Pause
- Request
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

## Mission Delete
- Request
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

## Process Update
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_update",
  "message_detail": {
    "download_info": null
  }
}
```

- Response
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

## Process Pause
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_finish",
  "message_detail": null
}
```

## Process Finish
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_finish",
  "message_detail": {
    "delete_file": false
  }
}
```

- Response
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