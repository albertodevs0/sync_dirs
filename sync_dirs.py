import argparse
import logging
import time
import os
import shutil


def delete_dirs(root, dirs, replica_folder, source_folder):
    for directory in dirs:

        # get the replica path and directory relative path
        replica_path = os.path.join(root, directory)
        relative_path = os.path.relpath(replica_path, replica_folder)

        # build the source path
        source_path = os.path.join(source_folder, relative_path)

        if not os.path.exists(source_path):

            # the file gets removed
            subdirectories = []
            for file in os.listdir(replica_path):

                if os.path.isdir(os.path.join(replica_path, file)):
                    subdirectories.append(file)
                elif os.path.isfile(os.path.join(replica_path, file)):
                    delete_files(replica_path, [file], replica_folder, source_folder)

            # if there are still subdirectories in this folder I simply keep on scanning until I don't find one anymore
            # mainly do this so that every delete is logged, otherwise could've avoided recursion and used
            # shutil.rmtree(replica_path)
            if subdirectories:
                delete_dirs(replica_path, subdirectories, replica_folder, source_folder)

            logging.info(f"The folder {replica_path} has been deleted")
            os.rmdir(replica_path)


def delete_files(root, files, replica_folder, source_folder):
    for file in files:

        # get the replica path and directory relative path
        replica_path = os.path.join(root, file)
        relative_path = os.path.relpath(replica_path, replica_folder)

        # build the source path
        source_path = os.path.join(source_folder, relative_path)

        if not os.path.exists(source_path):
            logging.info(f"The file {replica_path} has been deleted")
            os.remove(replica_path)


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
        delete_dirs(root, dirs, replica_folder, source_folder)
        delete_files(root, files, replica_folder, source_folder)


def main():
    # define parser
    data_parser = argparse.ArgumentParser(description="script used to continuously sync the directory content into "
                                                      "another")

    # define the parser arguments
    data_parser.add_argument("source_folder", help="the source folder to get the content from")
    data_parser.add_argument("replica_folder", help="the replica folder to copy the content to")
    data_parser.add_argument("--wait_time",
                             help="specify a waiting time between synchronizations (expressed in seconds)",
                             type=int, default=60)
    data_parser.add_argument("--logfile", help="specify a log file to record every event",
                             default="sync_log.log")

    # get the arguments values
    sync_arguments = data_parser.parse_args()

    # define the logger
    logging.basicConfig(level='INFO', format="%(asctime)s - [%(levelname)s] | %(message)s",
                        handlers=[logging.FileHandler(sync_arguments.logfile), logging.StreamHandler()])

    while True:
        logging.info("---- Synchronization started ----")
        sync_directories(sync_arguments.source_folder, sync_arguments.replica_folder)
        logging.info("---- Synchronization finished ----")
        time.sleep(sync_arguments.wait_time)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("---- Synchronization process stopped ----")
