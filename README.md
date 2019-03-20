### Description

Asynchronously downloads contents of provided OneDrive **shared** folder/file url without authentication. 

Works for:
- Linux (tested)
- Windows (tested)
- most probably also for MacOS (not tested)



### Usage

```python
from onedrive import OneDrive

# path could be relative to current working directory of script
# or absolute (e.g. C:\\Users\\Username\\Desktop, /home/username/Desktop)
folder = OneDrive(url="https://1drv.ms/f/s!ArwO5iEFDkD1jJNshhRIP-okHCS52g", path="Desktop")

# fire download
folder.download()
```

### Tips

If you wanna get only direct download link of shared file, just change the top level domain
of shared link from `.ms` to `.ws` (does not work for shared folder)
