# Palo Alto URL Filtering Profile Exporter

This script takes a firewall or Panorama configuration in XML format and outputs a CSV file **url_profiles.csv** with the following structure:

```
profile_name,category1,category2,category3
default,allow,alert,block
Alert_Only,alert,alert,alert
Strict,alert,block,block
```

This makes it easy to perform firewall audits and check that certain URL Categories are blocked or allowed for all profiles. Use the -i flag to transpose the CSV output, to have the profiles as columns and the URL Categories as rows.

File **builtin_categories.txt** contains the full list of predefined Palo Alto URL Categories so as to output a complete CSV even if some of them aren't explicitly configured in the URL Profiles. This is because the default action (Allow) for a certain URL Category does not show in the XML configuration unless it has been manually modified in the past, and this could cause the extract to miss displaying certain allowed websites. The file must be updated with any URL Categories Palo Alto releases in the future.

An empty entry for Custom URL Categories in the CSV is equivalent to an action of "None" and indicates that the Custom URL Category is not considered when filtering the traffic. The action for the predefined category of the website applies in this case.

### SCM Support

The script can now pull URL profiles from Strata Cloud Manager for exporting.

### Usage

```
usage: palo_url_exporter.py [-h] [-i] [-f FOLDER] [-s SNIPPET] [-k] config_file

positional arguments:
  config_file           The firewall or Panorama configuration in XML format. Input "scm" to connect to SCM instead.

options:
  -h, --help            show this help message and exit
  -i, --invert-csv      Invert rows with columns
  -f FOLDER, --folder FOLDER
                        SCM Folder. Default: All
  -s SNIPPET, --snippet SNIPPET
                        SCM Snippet. Default: folder All
  -k, --ignore-ssl      Ignore SSL Errors for SCM connection. Default: False
```
```
Example:

  $ python3 palo_url_exporter.py /home/user/Downloads/running-config.xml

  $ export SCM_CLIENT_ID=""
  $ export SCM_CLIENT_SECRET=""
  $ export SCM_TSG_ID=""
  $ python3 palo_url_exporter.py scm --folder Branch
```

The script has been tested with PanOS 10.1, PanOS 10.2, PanOS 11.1, SCM.

### Requirements

- [lxml](https://pypi.org/project/lxml/) (install with ```pip3 install lxml```)
- [pan-scm-sdk](https://pypi.org/project/pan-scm-sdk/) (install with ```pip3 install pan-scm-sdk```)

### License

This project is licensed under the [MIT License](LICENSE).
