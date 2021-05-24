# Download Info
> All analysis tools must implement the following two functions.

## get_base_file_info
> @:param filename: The name to save, which can be a file or directory.<br>
> @:param filesize: Sum of the file size in the resource.<br>
> @:param other: Self-defined according to different schema.
```json
{
  "filename": "",
  "filesize": 0,
  "other": {}
}
```

## get_current_finish_size
> @:return: Current downloaded file size.