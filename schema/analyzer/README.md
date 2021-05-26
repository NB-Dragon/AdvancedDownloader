# Download Info
> All analysis tools must implement the following two functions.

## get_download_info
> @:param total_size: Sum of the file size in `file_dict`.<br>
> @:param file_dict: Each file info.<br>
> @:param file_dict.file_name: The relative path to save in current resource.
```json
{
  "total_size": 0,
  "file_dict": {
    "relative_path": {
      "filesize": 0,
      "range": false,
      "section": []
    }
  }
}
```