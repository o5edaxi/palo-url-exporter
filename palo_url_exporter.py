"""This module reads a Palo Alto configuration in XML format and outputs a csv file of the form:
profile,category1,category2,category3
default,allow,alert,block
Alert_Only,alert,alert,alert
Strict,alert,block,block

usage: palo_urlcat_analyzer.py [-h] [-i] config_file"""

import csv
import argparse
from lxml import etree

XPATH_URLF_BASE = './/profiles/url-filtering/entry'
ACTIONS = ('allow', 'alert', 'block', 'continue', 'override')
# Default action for built-in categories, as it doesn't appear in the XML
# For custom categories it's always "None", so this value does not affect those
DEFAULT_BUILTINS_ACTION = 'allow'
# This list is populated with the contents of file "builtin_categories.txt"
BUILTINS = []
OUTPUT_FILE = 'url_profiles.csv'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read a Palo Alto configuration and output the URL'
                                                 ' Filtering profiles in a csv file showing '
                                                 'the respective action for each URL category.')
    parser.add_argument('-i', '--invert-csv', action='store_true', help='Invert rows with columns')
    parser.add_argument('config_file', type=str, help='The firewall or Panorama  configuration in '
                                                      'XML format.')
    args = parser.parse_args()
    root = etree.parse(args.config_file)
    with open('builtin_categories.txt', 'r', encoding='utf8') as builtins_file:
        for line in builtins_file:
            BUILTINS.append(line.rstrip())
    profiles_list = []
    for url_profile in root.findall(XPATH_URLF_BASE):
        profile_dict = {'profile_name': url_profile.attrib['name']}
        for action in ACTIONS:
            category_list = url_profile.findall(f'./{action}/member')
            for category in category_list:
                profile_dict[category.text] = action
        for builtin_cat in BUILTINS:
            if builtin_cat not in profile_dict:
                profile_dict[builtin_cat] = DEFAULT_BUILTINS_ACTION
        profiles_list.append(profile_dict)
    with open(OUTPUT_FILE, 'w', encoding='utf8', newline='') as output_file:
        fields_list = ['profile_name']
        alphabetic = []
        for column_name in set().union(*(d.keys() for d in profiles_list)):
            if column_name == 'profile_name':
                continue
            # Try to put custom categories first
            if column_name not in BUILTINS:
                fields_list.append(column_name)
            else:
                alphabetic.append(column_name)
        fields_list += sorted(alphabetic)
        dict_writer = csv.DictWriter(output_file, fieldnames=fields_list)
        dict_writer.writeheader()
        dict_writer.writerows(profiles_list)
    if args.invert_csv:
        with open(OUTPUT_FILE, 'r', encoding='utf8', newline='') as input_file:
            a = zip(*csv.reader(input_file))
        with open(OUTPUT_FILE, 'w', encoding='utf8', newline='') as output_file:
            csv.writer(output_file).writerows(a)
