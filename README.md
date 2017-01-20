# fts3-webdav-sync

Project to synchronize a source webdav to a destination webdav using fts3.

## Requirements
*   Python 2.7
*   Pip
*   System libraries
    +   GCC
    +   curl-dev
    +   musl-dev
    +   libxml2-dev
    +   libxslt-dev
    +   git
*   Running fts3 instance with installed rest-interface
    +   fts3: <http://fts3-docs.web.cern.ch/fts3-docs/>
    +   Installation guide for the rest interface: <http://fts3-docs.web.cern.ch/fts3-docs/fts-rest/docs/install.html>

## Execution

1.  Please adapt the config.yaml to fit your needs
    The possible parameters are described below.
    The minimal needed settings are:
    -   ``Essential settings``
        +   ``fts3 REST endpoint``
        +   ``source endpoint``
        +   ``destination endpoint``
    -   ``SSL settings``
        +   ``path of user certificate``
        +   ``path of user key``
2.  Install the needed dependencies:
    ```bash
    cd <cloned directory>
    # Avoids the following conflict:
    # 'pycurl: libcurl link-time ssl backend (xxx) is different from compile-time ssl backend (yyy) conflict
    export PYCURL_SSL_LIBRARY=openssl
    pip install -r requirements.txt
    ```
3.  Run the program
    ```bash
    python main.py --config <path to your config.yaml>
    ```

## Configuration parameters

### Essential settings
These are the core settings which have to be provided to run the synchronization:

*   ``fts3 REST endpoint``: URL of the rest endpoint of your fts3 instance
*   ``source endpoint``:
    -   URL of the webdav server which provides the data which should be synchronized to a target files.
       New or modified files are synchronized.
    -   HTTP and HTTPS are permitted protocols
    -   Example values:
        +   ``'http://my.webdav.com/'``
        +   ``'http://my.webdav.com:8080/'``
        +   ``'http://my.webdav.com:8090/any/sub/directory'``
*   ``destination endpoint``
    -   URL of the webdav server which should get the chanes from the source endpoint
    -   HTTP and HTTPS are permitted protocols
    -   Example values:
        +   ``'http://my.webdav.com/'``
        +   ``'http://my.webdav.com:8080/'``
        +   ``'http://my.webdav.com:8090/any/sub/directory'``

### SSL settings
Since FTS requires SSL the specification of ssl settings is needed.

*   ``path of user certificate``
    -   Path of the certificate to be used
    -   Example values:
        +   ``'/etc/ssl/mycert.cert'``
*   ``path of user key``
    -   Path of the key for the certificate
    -   Example values:
        +   ``'/etc/ssl/my_secret_key.key'``
*   ``verify host``
    -   Allows you to skip the verification of the host certificates
    -   Useful if you have deal with self signed certificates
    -   Possible values:
        +   ``True``: host is verified (default)
        +   ``False``: host is not verified

### Synchronization settings
More detailed configuration of the synchronization itself.

*   ``action for modified file``
    -   Specifies how to deal with modified files. Modified files are files which are already at the destination webdav,
    but in a different version than on the source webdav
    -   Possible values:
        +   ``'ignore'``: Modified files are not synchronized (default)
        +   ``'overwrite'``: The file on the destination dav is overwritten by the version of the source dav
        +   ``'keep_both'``: The file is synchronized, but not overwritten on the destination dav as the filename is changed to
            ``<old filename_(<etag of file>)<.datatype if existing>``
*   ``sync interval in minutes``
    -   Describes how often the synchronization is run (checking for changes, delegating it to fts3)
    -   The unit is minutes, so ``5`` means that the synchronization is executed every 5 minutes
    -   Possibles values:
        +   Int or Float (default: 30)
*   ``dry run``
    -   Shows you which changes have been detected and would be synced, but disables the actual file synchronization
    -   Useful if you want to have a look which changes would be made, but do not want actual changes
    -   Possible values:
        +   ``True``: Dry run is enabled, no files are actually synchronized
        +   ``False``: Dry run is disabled, files can be created / overwritten (default)
*   ``single run``
    -   The synchronization is only run once and therefore not repeated
    -   Possible values:
        +   ``True``: Run only once
        +   ``False``: Run in intervals (default)
*   ``exclude``
    -   Files / directories can be excluded from the synchronization
    -   Examples:
        +   ``'file.jpg'``: A file with the name ``file.jpg`` in the root directory of the synchronization is ignored
        +   ``'*/file.jpg'``: Every file with the name ``file.jpg`` is ignored (also in subdirectories)
        *   ``'*.log'``: Any file with the type ``log``is excluded
        *   ``'dir/*'``: The complete directory ``dir`` is ignored
        *   ``'dir/subdir/*'``: A subdirectory called ``subdir`` would be ignored if it is a subdir of `dir`
    -   Further documentation: <https://docs.python.org/2/library/fnmatch.html>


### DAV settings
Allows to configure the communication between the synchronization software and the webdav endpoints.

*   ``verbose``
    -   Enables verbose logging of the communication with the webdav endpoints
    -   Possible values:
        +   ``True``: verbose logging of the webdav communication is enabled
        +   ``False``: verbose logging of the webdav communication is disabled (default)

### Logging
Allows to specify the behaviour of the logging
*   ``log level``
    -   You can specify which events are logged
    -   Possible values:
        +   ``'DEBUG'``: (default) (much logging)
        +   ``'INFO'``
        +   ``'WARNING'``
        +   ``'ERROR'``
        +   ``'CRITICAL'``: (little logging)
*   ``path of logging file``
    -   You can specify where the log statements should be saved
    -   Possible values:
        +   Provide no path and log to the terminal (default)
        +   ``'path/to/the/logfile.txt'``
