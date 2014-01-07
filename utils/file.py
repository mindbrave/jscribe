# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re


def discover_files(input_paths, input_regex, ignore_paths_regex=[], ignore_regex=None):
    input_re = re.compile(input_regex)
    if ignore_regex is not None:
        ignore_re = re.compile(ignore_regex)
    # compile regex for ignore paths
    ignore_paths_regex_obj = []
    for path in ignore_paths_regex:
        ignore_paths_regex_obj.append(re.compile(path))
    file_paths = []
    for path in input_paths:
        for dirpath, dirnames, filenames in os.walk(path):
            if not _match_ignore_path(ignore_paths_regex_obj, dirpath):
                continue
            for filename in filenames:
                if ignore_regex is not None and ignore_re.match(filename):
                    continue
                if input_re.match(filename):
                    file_paths.append(os.path.join(dirpath, filename))
    return file_paths


def _match_ignore_path(ignore_paths_regex_obj, dirpath):
    for ignore_path_obj in ignore_paths_regex_obj:
        if ignore_path_obj.match(dirpath) is not None:
            return False
    return True


def get_source_file_coding(path):
    source_coding_re = re.compile(r'coding[:=]\s*(?P<coding>[-\w.]+)')
    source_coding = None
    with open(path, 'r') as f:
        for i in range(2):
            match_inst = source_coding_re.search(f.readline())
            if match_inst is not None:
                source_coding = match_inst.group('coding')
                break
        f.close()
    return source_coding