"""Download and prepare a reproducible QM9 subset for later preprocessing."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import pandas as pd
import yaml
from rdkit import Chem