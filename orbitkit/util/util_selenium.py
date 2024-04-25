import os
import datetime
import time


def is_chrome_download_success(check_dir, extension="", first_timeout=30, total_timeout=60 * 10):
    """
    :param check_dir: The folder to check.
    :param extension: Target extension.
    :param first_timeout: The fist time found no file exist.
    :param total_timeout: Total timeout.
    :return:
    """
    start_timestamp = datetime.datetime.now().timestamp()

    in_while = True
    file_path = ""
    while in_while:
        for root, dirs, files in os.walk(check_dir):
            if root != check_dir:
                break

            """
            len(files) < 1
            len(files) == 1
            len(files) > 1
            """

            # If there is no file exist but the spent time exceed "first_timeout" -> Exception
            if len(files) < 1:
                delta_sec = int(datetime.datetime.now().timestamp() - start_timestamp)
                if delta_sec > first_timeout:
                    raise Exception("Download no file timeout...")

            # If there is only 1 file exist and the extension if downloaded file is "c...d" -> keep downloading
            if len(files) == 1:
                if str(files[0]).lower().endswith(".crdownload"):
                    break

                # If there is only 1 file and the file satisfies the target extension -> download success
                if str(files[0]).lower().endswith(extension):
                    in_while = False
                    file_path = os.path.join(root, files[0])

            # If more than 1 file exist in specified folder -> Exception
            if len(files) > 1:
                raise Exception("Downloaded file exceed 1 file exception...")

        # Check by each break
        time.sleep(0.5)

        # If the total spent time exceed "total_timeout" -> exception
        delta_sec = int(datetime.datetime.now().timestamp() - start_timestamp)
        if delta_sec > total_timeout:
            raise Exception("Download timeout...")
    return file_path
