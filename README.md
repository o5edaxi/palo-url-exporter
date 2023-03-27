# Palo Alto URL Filtering Profile Exporter

This script takes a firewall or Panorama configuration in XML format and outputs a CSV file with the following structure:

```
profile_name,category1,category2,category3
default,allow,alert,block
Alert_Only,alert,alert,alert
Strict,alert,block,block
```

This makes it easy to perform firewall audits and check that certain URL Categories are blocked or allowed for all profiles. Use the -i flag to transpose the CSV output, to have the profile names as rows and the URL Categories as columns.

### Usage

```
Usage: palo_urlcat_analyzer.py [-h] [-i] config_file
```
```
Example:

  $ python3 palo_urlcat_analyzer.py /home/user/Downloads/running-config.xml
```

The script has been tested with PanOS 10.1.

### Requirements

- [lxml](https://pypi.org/project/lxml/) (install with ```pip3 install lxml```)

### License

This project is licensed under the [MIT License](LICENSE).
