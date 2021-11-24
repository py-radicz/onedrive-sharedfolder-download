### Description

Asynchronously downloads contents of provided OneDrive **shared** folder/file url without authentication. 

### Usage

```python
from onedrive import OneDriveSharedFolder

o = OneDriveSharedFolder("https://1drv.ms/u/s!AtZI6E5G7ZC_izG2o7OFNjh2N0Yk?e=hjDg8t")

# downloads with default path to storage which is CWD and default concurrent requests which is set to 5
o.download() 

# customize to your liking
o.download(path='/home/user/Downloads', concurrent_reqs=10)
```

### Tips

If you wanna get only direct download link of shared file, just change the top level domain
of shared link from `.ms` to `.ws` (does not work for shared folder)
