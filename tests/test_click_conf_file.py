"Basic tests"
from os.path import exists, join
from os import environ
from shutil import copyfile
from tempfile import TemporaryDirectory
import click
from click.testing import CliRunner
from click_conf_file import __version__, conf_option


def test_version():
    "Test Version"
    assert __version__ == "0.1.0"


def test_calls_callback(clirunner: CliRunner):
    "First verify that the callback is called when default value is used."

    some_dict = dict()

    def callback(_, __, val):
        "Callback"
        some_dict["happened"] = val
        return val

    @click.command("dorth")
    @click.option("-v", "--val", default="VAL", callback=callback)
    def a_command(_):
        "A command"
        ...

    clirunner.invoke(a_command, [])
    assert "happened" in some_dict
    assert some_dict["happened"] == "VAL"


def test_loads_config_when_path_given(conf1_path, clirunner: CliRunner):
    "The config file is loaded when given."

    that = dict()
    assert exists(conf1_path)

    @click.command("testapp")
    @conf_option(send_param=True)
    def testapp(config):
        "The test app"
        that["awesome"] = config
        assert "val1" in config

    result = clirunner.invoke(testapp, ["--config", conf1_path])
    assert result.exit_code == 0


def test_provides_value_for_param(conf1_path, clirunner: CliRunner):
    "Actually provides a value for configured parameters"

    @click.command("testapp")
    @click.option("-v", "--val1")
    @conf_option()
    def testapp(val1):
        "The test app"
        assert val1 == "YES"

    result = clirunner.invoke(testapp, ["--config", conf1_path])
    assert result.exit_code == 0


def test_looks_for_file_in_dirs(conf1_path, clirunner: CliRunner):
    "Actually provides a value for configured parameters"

    with TemporaryDirectory() as tempdir:
        environ["TESTAPP_CONFIGDIR"] = tempdir
        copyfile(conf1_path, join(tempdir, "testapp.conf"))

        @click.command("testapp")
        @conf_option(try_path="$TESTAPP_CONFIGDIR/testapp.conf")
        @click.option("-v", "--val1")
        def testapp(val1):
            "The test app"
            assert val1 == "YES"

        result = clirunner.invoke(testapp)
        assert result.exit_code == 0


# awesomeval = 54321
# nothingval = false
def test_okay_to_put_config_sections(conf2_path, clirunner: CliRunner):
    "Config sections named after the app will be added, but not others."

    @click.command("testapp")
    @conf_option(send_param=True)
    @click.option("-v", "--val1")
    @click.option("-a", "--awesomeval", type=int)
    def testapp(val1, awesomeval, config):
        "The test app"
        assert val1 == "YES"
        assert awesomeval == 12345
        assert "nothingval" not in config

    result = clirunner.invoke(testapp, ["--config", conf2_path])
    assert result.exit_code == 0
