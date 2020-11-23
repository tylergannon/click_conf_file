"Create fixtures"
from os import getcwd
from os.path import join
import pytest
from click.testing import CliRunner


@pytest.fixture()
def conf1_path():
    "Path to conf1.toml"
    return join(getcwd(), "tests", "fixtures", "conf1.toml")


@pytest.fixture()
def conf2_path():
    "Path to conf1.toml"
    return join(getcwd(), "tests", "fixtures", "conf2.toml")


@pytest.fixture()
def clirunner():
    "Build a CliRunner"
    return CliRunner()
