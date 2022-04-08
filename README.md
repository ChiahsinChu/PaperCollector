# PaperCollector

--

To Do List:

- [ ] extract DOI from txt/ris/html

--

This is a tiny package to:

- Automactically save ALL searching results of [`Web of Science (WOS)`](http://www.webofknowledge.com/?DestApp=WOS)
- Export DOIs from reference files
- Download the articles from [Sci-Hub](http://sci-hub.mksa.top) based on DOIs.

## Installation

```bash
python setpy.py install
```

## Usage

| Key               | Type       | Example                          | Description                                         |
| ----------------- | ---------- | -------------------------------- | --------------------------------------------------- |
| `executable_path` | Str        | "/usr/local/bin"                 | Path of browser driver                              |
| `wos_path`        | Str        | "./wos"                          | Path for saving downloaded reference files from WOS |
| `url`             | Str        | Page of searching results in WOS |                                                     |
| `username`        | Int or Str | -                                | Username for login                                  |
| `password`        | Int or Str | -                                | Password for login                                  |
| `institute`       | Str        | "Fake University"                | Name of institute                                   |
| `format`          | Str        | "ris"                            | Format of downloaded reference files                |
| `sortby`          | Str        | "Date: newest first"             | Default: Relevance                                  |
| `scihub_path`     | Str        | "./scihub"                       | Path for saving downloaded pdf files from Sci-Hub   |

### Download references from

```bash
ppclt wos params.json
```

```bash
ppclt doi params.json --save SAVE_PATH
```

```bash
ppclt pdf params.json --external DOIs.txt
```

## Reference

[WOS](https://blog.csdn.net/Parzival_/article/details/122360528)

[Download setup of selenium](https://blog.csdn.net/z15517303852/article/details/90579577)
