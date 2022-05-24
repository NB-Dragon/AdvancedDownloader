# Structure Define
- `file_info->uuid->file_size`: The value can only be number or null.
- `file_info->uuid->section_detail`: Inform the user of the source of file data.
- `section_info->uuid->section_size`: The value can only be number or null.
- `section_info->uuid->section_hash`: Inform the user about the hash of the section.
- `total_size`: Sum of the `section_info->uuid->section_size`.

# Example
```json
{
  "total_size": 0,
  "file_info": {
    "uuid(mission_uuid + file + 1)": {
      "file_size": 0,
      "save_path": "relative_path",
      "section_detail": {
        "uuid(mission_uuid + section + 1)": [
          "file_position", "section_position", "section_length"
        ],
        "uuid(mission_uuid + section + 2)": [
          "file_position", "section_position", "section_length"
        ]
      }
    },
    "uuid(mission_uuid + file + 2)": {
      "file_size": 0,
      "save_path": "relative_path",
      "section_detail": {
        "uuid(mission_uuid + section + 1)": [
          "file_position", "section_position", "section_length"
        ],
        "uuid(mission_uuid + section + 2)": [
          "file_position", "section_position", "section_length"
        ]
      }
    }
  },
  "section_info": {
    "uuid(mission_uuid + section + 1)": {
      "section_hash": "",
      "section_size": 0,
      "current_progress": []
    },
    "uuid(mission_uuid + section + 2)": {
      "section_hash": "",
      "section_size": 0,
      "current_progress": []
    }
  }
}
```

# Question
- How to confirm the download is over?
> The progress of all sections is an empty array.

- How to update this information while downloading?
> Only `current_progress` in `section_info` can be updated.
> Other information is dynamically calculated as needed.

- How to check if a file is complete?
> According to the prompt, take the specified location data
> in the real file to calculate the hash and compare it with `section_info`
