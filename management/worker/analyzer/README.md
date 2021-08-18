# Analyzer
> All analyze tools must implement the following functions.

## get_download_info
> @:param total_size: Sum of the section size.<br>
> @:param file_dict: All real documents.<br>
> @:param section_dict: All the unit, reference torrent.<br>
> @:param `file_position`, `section_start`, `section_end` are integer data.
```json
{
  "total_size": 0,
  "file_dict": {
    "uuid + namespace + file + 1": {
      "save_path": "relative_path",
      "file_size": [null, 0]
    },
    "uuid + namespace + file + n": {
      "save_path": "relative_path",
      "file_size": [null, 0]
    }
  },
  "section_dict": {
    "uuid + namespace + section + 1": {
      "progress": [],
      "file_mapping": {
        "file_hash_1": ["file_position", "section_start", "section_end"],
        "file_hash_n": ["file_position", "section_start", "section_end"]
      }
    },
    "uuid + namespace + section + n": {
      "progress": [],
      "file_mapping": {
        "file_hash_1": ["file_position", "section_start", "section_end"],
        "file_hash_n": ["file_position", "section_start", "section_end"]
      }
    }
  }
}
```