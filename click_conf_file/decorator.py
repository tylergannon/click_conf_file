"Creates the decorator to be used in click apps."
from __future__ import annotations
from typing import Optional, List, Iterable
from os.path import expanduser, expandvars, isfile, exists
from functools import partial
import toml
import click


LOOK_IN = ["$HOME/.{app_name}rc", "$HOME/.config/{app_name}/conf.toml"]


def expandall(app_name: str, path: str):
    "Expand user home and environment variables"
    return expandvars(expanduser(path.format(app_name=app_name)))


def callback(
    app_name: str,
    try_path: List[str],
    ctx: click.Context,
    param: click.Parameter,
    fpath: str,
) -> dict:
    "The callback to the click option which is configured in `params_from_conf`"
    app_name = app_name or ctx.info_name
    path_mapper = partial(expandall, app_name)
    if fpath is None:
        fpaths = list(filter(exists, map(path_mapper, try_path)))
        if len(fpaths) > 0:
            fpath = fpaths[0]
            if not isfile(fpath):
                raise click.BadParameter(
                    f"{fpath} exists but is not a file.", ctx=ctx, param=param
                )
    if fpath is None:
        return fpath

    with open(fpath) as infile:
        config = toml.load(infile)

    if ctx.default_map is None:
        ctx.default_map = dict()

    for name, value in config.items():
        if isinstance(value, dict) and name == app_name:
            for inner_name, inner_value in value.items():
                ctx.default_map.setdefault(inner_name, inner_value)
        else:
            ctx.default_map.setdefault(name, value)

    return config


def conf_option(  # pylint: disable=R0913
    app_name: str = None,
    param_names: Iterable[str] = ("-c", "--config"),
    send_param: bool = False,
    try_path: List[str] = None,
    is_eager: bool = True,
    show_default: bool = None,
):
    """
    Decorate click commands with the ability to load parameters from a
    configuration file.

    :param app_name: Name of app.  Defaults to name given to :function:`click.command`.
       Used for default config file names, as well as the section name in
       the config file.
    :param param_names: Forwarded to :function:`click.option` to determine the name
        of the CLI param that will be used to specify the path to the conf file.
    :param send_param: If True, passes the object loaded from the config file.
        This will result in an argument being given to the app function, named
        after the parameters as given in `param_names`.
    :param try_path: A path or list of paths, where the app should look for config
        files.  Environment variables and User home (~) will be expanded.

        By default, it will already look at `~/.{app_name}rc` and
        `~/.config/{app_name}/conf.toml`.  Anything given in this parameter
        will be added to the front of this list.

        .. note:: Only one configuration file will be loaded regardless of how many exist.
    :param is_eager: Forwarded to :function:`click.option`.  If you don't know why
        you'd need this, you probably don't.
    """
    try_path = (
        []
        if try_path is None
        else try_path
        if isinstance(try_path, list)
        else [try_path]
    ) + LOOK_IN

    # Add default path locations to help text, either if requested,
    # or else if not specifically declined but app_name was given.
    if app_name is not None:
        try_path = [path.format(app_name=app_name) for path in try_path]
    if show_default is None:
        show_default = app_name is not None
    help_text = "Optional TOML conf file path."
    default_text = (
        show_default
        if isinstance(show_default, str)
        else "Look in " + ", ".join(try_path)
    )

    def decorator(function):
        "The decorator."
        click_opt = click.option(
            *param_names,
            type=click.Path(exists=True, dir_okay=False),
            expose_value=send_param,
            callback=partial(callback, app_name, try_path),
            is_eager=is_eager,
            default=lambda: None,
            help=help_text,
            show_default=(default_text if show_default else False),
        )
        return click_opt(function)

    return decorator
