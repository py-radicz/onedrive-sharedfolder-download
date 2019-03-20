### Usage

```python
from onedrive import OneDrive

# path could be relative to current working directory of script
# or absolute
folder = OneDrive(url="https://xxx.zzz", path="Desktop")

# fire download
folder.download()
```


