# Create: Create Download Mission
## General usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp"
```

## Headers usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --headers "accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Origin: https://www.google.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
```

## Proxy usage
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --proxy "127.0.0.1:8888"
```

## Modify the number of threads
```Text
create --url "https://github.com/NB-Dragon/AdvancedDownloader/archive/refs/heads/master.zip" --output "/tmp" --thread 8
```

# Show: Query Download Mission
## Show the summary of all missions
```Text
show --all
```

## Show the details of the specific mission
```Text
show --mission-uuid mission_uuid
```

# Start: Start Download Mission
## Start all the missions
```Text
start --all
```

## Start the specific mission
```Text
start --mission-uuid mission_uuid
```

# Pause: Pause Download Mission
## Pause all the missions
```Text
pause --all
```

## Pause the specific mission
```Text
pause --mission-uuid mission_uuid
```

# Delete: Delete Download Mission
## Delete all the missions
```Text
delete --all [--with-file]
```

## Delete the specific mission
```Text
delete --mission-uuid mission_uuid [--with-file]
```

# Exit: Programme Exit
```Text
exit
```
