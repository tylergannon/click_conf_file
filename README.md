# click_conf_file

Use configuration files to set defaults for options on
[click](https://click.palletsprojects.com/en/7.x/) apps.

This is a quick rewrite of Philipp Hack's [click_config_file](https://github.com/phha/click_config_file),
improved to support default conf file locations.

## Installation

```
pip install click_conf_file
```


## Usage

```python
import click
from click_conf_file import conf_option

@click.command("testapp")
@click.option("--val1")
@click.option("--val2")
@conf_option()
def testapp(val1, val2):
  ...
```


