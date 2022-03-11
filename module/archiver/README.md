# Thread Archive Module: thread-archive
## Create Request
- Request
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

## Archive Request
- Request
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

- Response
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

## Query Request
- Request
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

- Response
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

## Delete Request
- Request
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