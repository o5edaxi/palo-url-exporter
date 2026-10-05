"""This module reads a Palo Alto configuration in XML format and outputs a csv file of the form:
profile_name,category1,category2,category3
default,allow,alert,block
Alert_Only,alert,alert,alert
Strict,alert,block,block

usage: palo_urlcat_analyzer.py [-h] [-i] config_file"""

import csv
import argparse
import os
import sys
from scm.client import Scm
from scm.config.security import URLAccessProfile
from lxml import etree

XPATH_URLF_BASE = './/profiles/url-filtering/entry'
ACTIONS = ('allow', 'alert', 'block', 'continue', 'override')
# Default action for built-in categories, as it doesn't appear in the XML
# For custom categories it's always "None", so this value does not affect those
DEFAULT_BUILTINS_ACTION = 'allow'
# This list is populated with the contents of file "builtin_categories.txt"
BUILTINS = []
SCM_KEYWORD = 'scm'  # Magic argument to switch to SCM mode
OUTPUT_FILE = 'url_profiles.csv'


def get_url_filtering_profiles(cid, sec, tsg, ver, folder_name: str):
    """
    Retrieves a list of URL filtering profiles for a specified folder in SCM.
    """
    
    # 1. Initialize the SCM Client
    # It is highly recommended to pull credentials from environment variables 
    # rather than hardcoding them in your script.
    client = Scm(
        cid,
        sec,
        tsg,
        verify_ssl=ver
    )

    # 2. Instantiate the URL Access Profile service
    url_profiles_service = URLAccessProfile(client)

    # 3. Retrieve the list of profiles
    try:
        # The list() method fetches the profiles assigned to the given folder
        profiles = url_profiles_service.list(folder=folder_name)
        print(f"Found {len(profiles)} URL Filtering profiles in folder '{folder_name}'")
        output = []
        for profile in profiles:
            # Initialize dictionary with the base profile name
            prof_dict = {'profile_name': profile.name}
            
            # Map the desired string values to their corresponding profile attributes
            actions = {
                'allow': profile.allow,
                'alert': profile.alert,
                'block': profile.block,
                'redirect': profile.redirect,
                'continue': getattr(profile, 'continue', [])  # Default to [] if attribute is missing
            }
            
            # Iterate through the mapping
            for action_name, categories in actions.items():
                if categories:  # Checks if not None and not empty
                    for category in categories:
                        prof_dict[category] = action_name
            output.append(prof_dict)
        return output

    except Exception as e:
        print(f"Error retrieving profiles: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read a Palo Alto configuration and output the URL'
                                                 ' Filtering profiles in a csv file showing '
                                                 'the respective action for each URL category.')
    parser.add_argument('-i', '--invert-csv', action='store_true', help='Invert rows with columns')
    parser.add_argument('-f', '--folder', type=str, default='All', help='SCM Folder. Default: All')
    parser.add_argument('-s', '--snippet', type=str, default=None, help='SCM Snippet. Default: folder All')
    parser.add_argument('-k', '--ignore-ssl', action='store_false', help='Ignore SSL Errors for SCM connection. Default: False')
    parser.add_argument('config_file', type=str, help='The firewall or Panorama  configuration in '
                                                      'XML format.')
    args = parser.parse_args()
    USE_SCM = True if args.config_file == SCM_KEYWORD else False
    with open('builtin_categories.txt', 'r', encoding='utf8') as builtins_file:
        for line in builtins_file:
            BUILTINS.append(line.rstrip())
    profiles_list = []
    if USE_SCM:
        client_id=os.environ.get("SCM_CLIENT_ID")
        client_secret=os.environ.get("SCM_CLIENT_SECRET")
        tsg_id=os.environ.get("SCM_TSG_ID")
        if not all((client_id, client_secret, tsg_id)):
            print('Missing credentials. Provide environment variables SCM_CLIENT_ID, SCM_CLIENT_SECRET, and SCM_TSG_ID. Exiting...')
            sys.exit(1)
        profiles_list = get_url_filtering_profiles(client_id, client_secret, tsg_id, args.ignore_ssl, args.snippet if args.snippet else args.folder)
        for profile in profiles_list:
            for builtin_cat in BUILTINS:
                if builtin_cat not in profile:
                    profile[builtin_cat] = DEFAULT_BUILTINS_ACTION
    else:
        root = etree.parse(args.config_file)
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
