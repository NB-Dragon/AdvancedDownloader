# Thread Control Module: thread-control
## Data Response
- Request
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

## Mission Start
- Request
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

- Response Fail
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

## Mission Pause
- Request
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

## Mission Delete
- Request
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

## Process Update
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_update",
  "detail": {
    "download_info": null
  }
}
```

## Process Pause
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_finish",
  "detail": null
}
```

## Process Finish
- Request
```json
{
  "mission_uuid": "",
  "message_type": "process_finish",
  "detail": {
    "delete_file": false
  }
}
```