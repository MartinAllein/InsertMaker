
class File:

    @staticmethod
    def set_file_extenstion(filename: str, extension: str) -> str:
        if not extension[0] == '.':
            extension = "." + extension

        # Set extension of filename to requested extension
        if filename[-(len(extension)):] != extension:
            filename += extension

        return filename
