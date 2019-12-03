import io
import json
import logging
import os
import re

import util.http as httpUtil

# key is source_url, value is target_url
rewrite_url = {}


def add_rewrite_url(source_url, target_url):
    rewrite_url[source_url] = target_url


def add_rewrite_url_path_param(source_url, target_url):
    '''source_url parameter placeholder syntax is {} or : and target_url parameter substituition syntax is $1 $ 2 etc.'''
    rewrite_url[source_url] = target_url


# key is source_url re, value is target_url
rewrite_url_regex = {}


def add_rewrite_url_regex(source_url, target_url):
    rewrite_url_regex[re.compile(source_url, re.IGNORECASE)] = target_url


def get_rewrite_url(incoming_url) -> str:
    logging.debug("enter rewrite: "+incoming_url)
    url = incoming_url.split('?')
    front_url = url[0]
    back_url = url[1] if len(url) > 1 else None
    ret_url = incoming_url
    found = False
    for source_url, target_url in rewrite_url.items():
        if front_url == source_url:
            ret_url = target_url
            found = True
        else:
            actual_token = front_url.split("/")
            source_url_token = source_url.split("/")
            if len(actual_token) == len(source_url_token):
                param_list = []
                for index, item in enumerate(source_url_token):
                    match = httpUtil.place_holder_re.match(item)
                    if match:
                        found = True
                        param_list.append(actual_token[index])
                    elif item != actual_token[index]:
                        found = False
                        break
                    else:
                        found = True
                if found:
                    actual_target = target_url
                    for index, item in enumerate(param_list):
                        actual_target = actual_target.replace("$"+str(index+1), item)
                    ret_url = actual_target

        if found:
            break

    if found and back_url is not None:
        ret_url = "".join([ret_url, "?", back_url])
    elif not found:
        ret_url = get_rewrite_url_regex(ret_url)
    logging.debug("exit rewrite: "+ret_url)
    return ret_url


def get_rewrite_url_regex(incoming_url) -> str:
    logging.debug("enter rewrite regex: "+incoming_url)
    url = incoming_url.split('?')
    front_url = url[0]
    back_url = url[1] if len(url) > 1 else None
    ret_url = incoming_url
    found = False
    for source_url_regex, target_url in rewrite_url_regex.items():
        match = source_url_regex.match(front_url)
        if match:
            ret_url = target_url
            found = True
            break
    if found and back_url is not None:
        ret_url = "".join([ret_url, "?", back_url])
    logging.debug("exit rewrite regex: "+ret_url)
    return ret_url


REWRITE_MODE = {
    "D": "direct",
    "R": "regex",
    "P": "path_param"
}


def get_rewrite_rules(config, dbPool) -> dict:
    enable = config['UrlRewriteConfig']['Enable']
    file = "".join([os.getcwd(), os.path.sep, config['UrlRewriteConfig']['File']])
    if not enable or (file is None or not (os.path.isfile(file) and os.path.exists(file))):
        return None

    with io.open(file, mode="r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    return data
