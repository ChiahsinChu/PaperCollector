# PaperCollector

This is a tiny package to:

- Automactically save ALL searching results of [`Web of Science (WOS)`](http://www.webofknowledge.com/?DestApp=WOS)
- Export DOIs from reference files
- Download the articles from [Sci-Hub](http://sci-hub.mksa.top) based on DOIs.

## Installation

```bash
python setpy.py install
```

## User guide

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

### Download references from WOS

```bash
ppclt wos params.json
```

### Extract DOIs from reference files

```bash
ppclt doi params.json
```

Optional argument:
`--save [SavePath]`: save path for `DOIs.txt`. If not provided, save files in the `wos_path`.
`--external [RefFiles]`: reference file(s). Wildcard is supported (e.g., `./test/ref-*.xls`).

### Download PDF files from Sci-Hub

```bash
ppclt pdf params.json --external DOIs.txt
```

Optional argument:
`--external [RefFiles]`: reference file(s). Wildcard is supported (e.g., `./test/ref-*.xls`).

## Developer guide

The main idea of this package is to use [`selenium`](https://www.selenium.dev/documentation/webdriver/) to finish some actions (e.g., click and send keys) on the browser.
This means that, if the proceduce (for example, for login) is different for you, you might need to make some modifications on the codes.
Besides, you might also want to create your own workflow for other websites/assignments.
If so, you should be interested in the following part.

### login

In this package, the workflow to download reference files from WOS starts with login via institute.
If you want to set a different login pathway, for example, by changing your institue, you need to rewrite the `WOS._login` method in `papercollector.main`.
Specifically, you need to change the XPATH or CSS_SELECTOR of the elements your should click/send keys.
You can find some tutorials in Google for how to find them (e.g., [Find XPATH in Chrome](https://www.scrapestorm.com/tutorial/how-to-find-xpath-in-chrome)).

### new workflow

You might want to download reference from the websites other than WOS.
Then you can add a new class analogous to `WOS` in `papercollector.main`.

## Reference

[WOS](https://blog.csdn.net/Parzival_/article/details/122360528)

[Download setup of selenium](https://blog.csdn.net/z15517303852/article/details/90579577)

---

To Do List:

- [ ] set background or not in json file

---
