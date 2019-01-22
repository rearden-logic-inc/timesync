import pkg_resources


def load_plugin(group, name):
    """
    Load the plugin from setuptools entry points.
    :param group: entrypoint group name
    :param name: name of the plugin
    :return: method that is defined.
    """
    plugin = None
    for entry_point in pkg_resources.iter_entry_points(group, name):
        plugin = entry_point.load()

        if plugin is not None:
            break

    if plugin is None:
        raise RuntimeError(f'Could not find plugin {name} in {group}')

    return plugin
