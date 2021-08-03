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

import numpy as np
import constph
import pytest

def test_test():
    """test for pytest in vstudio
    """
    assert "test" == "test"

def test_fill_dataclass():
    """Fill dataclass with input from the example.yaml in /test_data
    """
    
