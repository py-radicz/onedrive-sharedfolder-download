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
# or absolute
folder = OneDrive(url="https://xxx.zzz", path="Desktop")

# fire download
folder.download()
```


