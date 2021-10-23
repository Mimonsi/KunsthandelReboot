import os

from flask import current_app

from kunsthandel.main import utils


def get_database_usage():
    database_path = current_app.config.get("STORAGE_DATABASE_FILE")
    database_size = os.path.getsize(os.path.join(current_app.root_path, database_path))
    return "Database", str(database_path), utils.format_filesize(database_size), database_size


def get_directory_usage(local_path, name="Directory"):
    full_path = os.path.join(current_app.root_path, local_path)

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(full_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return name, str(local_path), utils.format_filesize(total_size), total_size