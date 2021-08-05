# Analyzer
> All analyze tools must implement the following functions.

## get_download_info
> @:param total_size: Sum of the file size in `file_dict`.<br>
> @:param file_dict: Each file info.<br>
> @:param file_dict.file_name: The relative path to save in current resource.
```json
{
  "total_size": 0,
  "file_dict": {
    "relative_path_1": {
      "filesize": 0,
      "range": false,
      "section": []
    },
    "relative_path_2": {
      "filesize": 0,
      "range": false,
      "section": []
    },
    "relative_path_n": {
      "filesize": 0,
      "range": false,
      "section": []
    }
  }
}
```