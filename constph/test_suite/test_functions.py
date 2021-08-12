"""
Unit and regression test for constant_pH.
"""

import copy
import logging
import os
import pathlib
import shutil
import subprocess
import sys

import constph
import pytest

from constph import (
    load_config_yaml)

def test_read_yaml():
    """Sample test, will check ability to read yaml files"""
    settingsMap = load_config_yaml(
        config="constph/test_suite/test_data/example.yaml",
        input_dir=".",
        output_dir='data/',
    )

    assert settingsMap["system"]["structure"]["name"] == '2OJ9-test1'
    settingsMap['bin_dir'] == 'constph/bin'
    
