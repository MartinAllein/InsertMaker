import os


class File:

    @classmethod
    def path_and_extension(cls, path: str, filename: str, extension: str) -> str:
        return os.path.join(path, cls.set_file_extension(filename, extension))

    @staticmethod
    def set_svg_extension(filename: str) -> str:
        return File.set_file_extension(filename, "svg")

    @staticmethod
    def set_config_extension(filename: str) -> str:
        return File.set_file_extension(filename, "config")

    @staticmethod
    def set_file_extension(filename: str, extension: str) -> str:
        if not extension[0] == '.':
            extension = "." + extension

        # Set extension of filename to requested extension
        if filename[-(len(extension)):] != extension:
            filename += extension

        return filename
