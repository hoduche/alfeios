# Fs-crawler

### Crawl your file system to check duplicated files
___

You need space on your hard drive ?
Fs-crawler can crawl your file system and list all duplicated files you can safely remove as well as the space you can gain.

You want to give a new life to your old hard drive but you're not sure all its content has been saved on your new hard drive ?
Fs-crawler can crawl your two drives and list all files on the old one that are not present on the new one. 

## Install

#### From GitHub
To install Fs-crawler from GitHub:
1. Run:
    ```
    git clone https://github.com/hoduche/fs-crawler
    ```
2. Inside the newly created fs-crawler folder, run (with Python 3 and setuptools):
    ```
    python setup.py install
    ```

## Run

#### As a Python module

```python
import pathlib

import fs_crawler.crawl as fsc

folder_path = pathlib.Path('M:/Pictures')
listing, tree = fsc.crawl(folder_path)
duplicates, size_gain = fsc.get_duplicates(listing)
fsc.dump_json_listing(duplicates, folder_path / 'duplicates.json')
print(f'you can gain {size_gain / 1E9:.2f} Gigabytes space')
```
