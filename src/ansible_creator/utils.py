"""Re-usable utility functions used by this package."""

from __future__ import annotations

import logging
import os
import sys

from typing import TYPE_CHECKING

from ansible_creator.exceptions import CreatorError


if TYPE_CHECKING:
    from importlib import abc

    from ansible_creator.templar import Templar

PATH_REPLACERS = {
    "network_os": "collection_name",
    "resource": "resource",
}

if sys.version_info < (3, 10):
    import importlib_resources as resources
else:
    from importlib import resources

logger = logging.getLogger("ansible-creator")


def get_file_contents(directory: str, filename: str) -> str:
    """Return contents of a file.

    :param directory: A directory within ansible_creator package.
    :param filename: Name of the file to read contents from.

    :returns: Content loaded from file as string.

    :raises FileNotFoundError: if filename cannot be located
    :raises TypeError: if invalid type is found
    :raises ModuleNotFoundError: if incorrect package is provided
    """
    package: str = f"ansible_creator.{directory}"

    try:
        with resources.files(package).joinpath(filename).open(
            "r",
            encoding="utf-8",
        ) as file_open:
            content: str = file_open.read()
    except (FileNotFoundError, TypeError, ModuleNotFoundError) as exc:
        msg = "Unable to fetch file contents.\n"
        raise CreatorError(msg) from exc

    return content


def copy_container(
    source: str,
    dest: str,
    templar: Templar | None = None,
    template_data: dict[str, str] | None = None,
    allow_overwrite: list[str] | None = None,
) -> None:
    """Copy files and directories from a possibly nested source to a destination.

    :param source: Name of the source container.
    :param dest: Absolute destination path.
    :param templar: An object of template class.
    :param template_data: A dictionary containing data to render templates with.
    :param allow_overwrite: A list of paths that should be overwritten at destination.

    :raises CreatorError: if allow_overwrite is not a list.
    """
    logger.debug("starting recursive copy with source container '%s'", source)
    logger.debug("allow_overwrite set to %s", allow_overwrite)

    def _recursive_copy(root: abc.Traversable) -> None:
        """Recursively traverses a resource container and copies content to destination.

        :param root: A traversable object representing root of the container to copy.
        """
        logger.debug("current root set to %s", root)

        for obj in root.iterdir():
            overwrite = False
            dest_name = str(obj).split(source + "/", maxsplit=1)[-1]
            dest_path = os.path.join(dest, dest_name)
            if (allow_overwrite) and (dest_name in allow_overwrite):
                overwrite = True

            # replace placeholders in destination path with real values
            for key, val in PATH_REPLACERS.items():
                if key in dest_path and template_data:
                    dest_path = dest_path.replace(key, template_data.get(val, ""))

            if obj.is_dir():
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)

                # recursively copy the directory
                _recursive_copy(root=obj)

            elif obj.is_file():
                # remove .j2 suffix at destination
                dest_file = os.path.join(dest, dest_path.split(".j2", maxsplit=1)[0])
                logger.debug("dest file is %s", dest_file)

                # write at destination only if missing or belongs to overwrite list
                if not os.path.exists(dest_file) or overwrite:
                    content = obj.read_text(encoding="utf-8")

                    # only render as templates if both of these are provided
                    # templating is not mandatory
                    if templar and template_data:
                        content = templar.render_from_content(
                            template=content,
                            data=template_data,
                        )
                    with open(dest_file, "w", encoding="utf-8") as df_handle:
                        df_handle.write(content)

    _recursive_copy(root=resources.files(f"ansible_creator.resources.{source}"))
