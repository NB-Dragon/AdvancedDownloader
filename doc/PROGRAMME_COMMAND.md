# Create: Create a task
## General Usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp"
```

## Headers Usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --headers "accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Origin: https://www.google.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
```

## Proxy Usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --proxy "127.0.0.1:8888"
```

## Modify the number of threads
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --thread 8
```

# Start: Start a task
```Text
start mission_uuid
```

# Pause: Pause a task
```Text
pause mission_uuid
```

# Delete: Delete a task
## Delete without file
```Text
delete mission_uuid 0
```

## Delete with file
```Text
delete mission_uuid 1
```

## Exit: Programme Exit
```Text
exit
```
