# Thread Archive Module: thread-archive
## Create Request
- Request
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "create_request",
    "message_detail": {
      "mission_info": null
    }
  }
}
```

## Show Request
- Request
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

## Delete Request
- Request
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "delete_request",
    "message_detail": {
      "with_file": false
    }
  }
}
```

## Archive Request
- Request
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

- Response
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

## Query Request
- Request
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

- Response
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

## Update Request
- Request
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

## State Request
- Request
```json
{
  "receiver": "thread-archive",
  "value": {
    "mission_uuid": "",
    "message_type": "state_request",
    "message_detail": {
      "mission_state": "sleeping|analyzing|running"
    }
  }
}
```
