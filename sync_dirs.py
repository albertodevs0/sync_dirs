import argparse
import logging
import time
import os
import shutil


def sync_directories(source_folder, replica_folder):
    for root, dirs, files in os.walk(source_folder):
        for directory in dirs:

            # get the source path and directory relative path
            source_path = os.path.join(root, directory)
            relative_path = os.path.relpath(source_path, source_folder)

            # build the replica path
            replica_path = os.path.join(replica_folder, relative_path)

            # check if the directory already exists
            if not os.path.exists(replica_path):
                os.makedirs(replica_path)
                logging.info(f"The folder {replica_path} has been created")

        for file in files:

            # get the source path and file relative path
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, source_folder)

            # build the replica path
            replica_path = os.path.join(replica_folder, relative_path)

            # check if the file already exists
            if not os.path.exists(replica_path):
                shutil.copy2(source_path, replica_path)
                logging.info(f"The file {replica_path} has been created")

            elif os.path.getmtime(source_path) > os.path.getmtime(replica_path):
                shutil.copy2(source_path, replica_path)
                logging.info(f"The file {replica_path} has been updated")

    for root, dirs, files in os.walk(replica_folder):
        for directory in dirs:

            # get the replica path and directory relative path
            replica_path = os.path.join(root, directory)
            relative_path = os.path.relpath(replica_path, replica_folder)

            # build the source path
            source_path = os.path.join(source_folder, relative_path)

            if not os.path.exists(source_path):

                # todo: when removing a directory that is populated, the parent dir doesn't get removed instantly
                try:
                    os.rmdir(replica_path)
                    logging.info(f"The folder {replica_path} has been deleted")
                except:
                    sync_directories(source_path, replica_path)

        for file in files:

            # get the replica path and file relative path
            replica_path = os.path.join(root, file)
            relative_path = os.path.relpath(replica_path, replica_folder)

            # build the source path
            source_path = os.path.join(source_folder, relative_path)

            # check if the file still exists
            if not os.path.exists(source_path):
                os.remove(replica_path)
                logging.info(f"The file {replica_path} has been deleted")


def main():
    # define parser
    data_parser = argparse.ArgumentParser(description="This is a program that can be used to sync two directories")

    # define the parser arguments
    data_parser.add_argument("source_folder", help="The source folder to get the content from")
    data_parser.add_argument("replica_folder", help="The replica folder to copy the content to")
    data_parser.add_argument("--time",
                             help="Specify how much time it will pass before repeating the synchronization process (it is expressed in seconds)",
                             type=int, default=60)
    data_parser.add_argument("--logfile", help="Specify a log file for the logging", default="sync_log.log")

    # get the arguments values
    sync_arguments = data_parser.parse_args()

    # define the logger
    logging.basicConfig(level='INFO', format="%(asctime)s - [%(levelname)s] | %(message)s",
                        handlers=[logging.FileHandler(sync_arguments.logfile), logging.StreamHandler()])

    while True:
        logging.info("Synchronization started")
        sync_directories(sync_arguments.source_folder, sync_arguments.replica_folder)
        logging.info("Synchronization finished")
        time.sleep(sync_arguments.time)


if __name__ == '__main__':
    main()
