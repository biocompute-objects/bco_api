# --- SOURCES --- #

# For finding files.
import glob

# For writing.
import os


# --- MAIN --- #

class FileUtils:



    def pathalizer(self, directory, pattern):

        # Description
        # -----------

        # Construct a search path with regex.

        # Arguments
        # ---------

        # directory
        # ---------
        #
        # Description:  where to look within the project directory.
        # Values:  any folder

        # pattern
        # -------
        #
        # Description:  the regex.
        # Values:  any regex

        # Outputs
        # -------

        # A directory + pattern string.
        #print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), directory + pattern))
        # Kick back the string.
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), directory + pattern)



    def create_files(self, payload, output_directory, file_extension):

        # Description

        # Write a list of files a list of files in a directory matching a regex.

        # Arguments

        # payload
        # ----------------
        #
        # Description:  what are we writing?
        # Values:  must be a dictionary where the keys are *ORIGINAL*  full file names and values are file contents.

        # output_directory
        # ----------------
        #
        # Description:  where are we writing to?
        # Values:  any extant directory - MUST BE AN ABSOLUTE PATH

        # file_extension
        # ----------------
        #
        # Description:  what extension are we appending to the *ORIGINAL* file name?
        # Values:  any string

        # Outputs

        # A list of files.

        # Construct the output path for each file and write.
        for original_filename, contents in payload.items():
            with open(self.pathalizer(output_directory, original_filename + file_extension), mode='w') as f:
                f.write(contents)



    def find_files(self, input_directory, regex):

        # Description

        # Retrieve a list of files in a directory matching a regex.

        # Arguments

        # input_directory
        # ----------------
        #
        # Description:  where are the files we're assigning?
        # Values:  any extant directory - MUST BE AN ABSOLUTE PATH

        # regex
        # ----------------
        #
        # Description:  what regex are we using to search the directory?
        # Values:  any regex

        # Outputs

        # A list of matching files.

        # Search the input directory for matching files.

        # Source:  https://stackoverflow.com/questions/39293968/python-how-do-i-search-directories-and-find-files-that-match-regex
        # Source:  https://stackoverflow.com/questions/30218802/get-parent-of-current-directory-from-python-script

        return glob.glob(self.pathalizer(input_directory, regex))


    # Find the entire tree of a folder based on an extension.
    def get_folder_tree_by_extension(self, search_folder, search_extension):

        # search_folder: where we're looking.
        # search_extension: the extension we're looking for.

        # Source: https://www.tutorialspoint.com/python/os_walk.htm

        # Set the root directory.
        root_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), search_folder)

        # Create a dictionary to return.
        returning = {'root_directory': root_directory, 'paths': []}

        for root, dirs, files in os.walk(root_directory):
            for name in files:
                returning['paths'].append(os.path.join(root, name))
            for name in dirs:
                returning['paths'].append(os.path.join(root, name))

        returning['paths'] = [x for x in returning['paths'] if x.find(search_extension) != -1]

        return returning


    # Find the entire tree of a folder, regardless of extension.
    def get_folder_tree(self, search_folder):

        # search_folder: where we're looking.

        # Source: https://www.tutorialspoint.com/python/os_walk.htm

        # Set the root directory.
        root_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), search_folder)

        # Create a dictionary to return.
        returning = {'root_directory': root_directory, 'paths': []}

        for root, dirs, files in os.walk(root_directory):
            for name in files:
                returning['paths'].append(os.path.join(root, name))
            for name in dirs:
                returning['paths'].append(os.path.join(root, name))

        returning['paths'] = [x for x in returning['paths'] if 1]

        return returning
