```
Usage: uploader.py [OPTIONS] FILE

  Wrapper for gpg and the pixeldrain API to upload files to pixeldrain
  encrypted, provide file to upload as argument, - to use stdin

Options:
  -n, --name TEXT         Filename for pixeldrain
  -k, --apikey TEXT       API key for pixeldrain NOTE: This argument is
                          mutually exclusive with  arguments: [secrets].
  -p, --passphrase TEXT   GPG symmetric passphrase NOTE: This argument is
                          mutually exclusive with  arguments: [secrets].
  -s, --secrets FILENAME  yaml file, can contain apikey and passphrase NOTE:
                          This argument is mutually exclusive with  arguments:
                          [passphrase, apikey].
  --help                  Show this message and exit.
```
