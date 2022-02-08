#!import wmi
#!# Initializing the wmi constructor
#!f = wmi.WMI()
#!# Printing the header for the later columns
#!print("pid Process name")
#!# Iterating through all the running processes
#!for process in f.Win32_Process():
#!	# Displaying the P_ID and P_Name of the process
#!	print(f"{process.ProcessId:<10} {process.Name}")


#-----------
#!import os
#!# Running the aforementioned command and saving its output
#!output = os.popen('wmic process get description, processid').read()
#!# Displaying the output
#!print(output)


#------------

#! # import module
#!import subprocess
#!# traverse the software list
#!Data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
#!a = str(Data)
#!# try block
#!# arrange the string
#!try:
#!  for i in range(len(a)):
#!    print(a.split("\\r\\r\\n")[i])
#!except IndexError as e:
#!   print("All Done")

#--------------

#!https://stackoverflow.com/questions/2212643/python-recursive-folder-read#2212698

#!...
import os
import sys

walk_dir =  'C:\\projects\\acm\\Nov2021\\azure-building-blocks\\terraform\\calls-to-modules\\instances\\ad-admin\\admin-pipelineAgents-ad-admin'
 #sys.argv[1]

print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

for root, subdirs, files in os.walk(walk_dir):
    print('--\nroot = ' + root)
    list_file_path = os.path.join(root, 'my-directory-list.txt')
    print('list_file_path = ' + list_file_path)

    with open(list_file_path, 'wb') as list_file:
        for subdir in subdirs:
            print('\t- subdirectory ' + subdir)

        for filename in files:
            file_path = os.path.join(root, filename)

            print('\t- file %s (full path: %s)' % (filename, file_path))

            with open(file_path, 'rb') as f:
                f_content = f.read()
                list_file.write(('The file %s contains:\n' % filename).encode('utf-8'))
                list_file.write(f_content)
                list_file.write(b'\n')
#!...

def isFileLocked(filePath):
    '''
    Checks to see if a file is locked. Performs three checks
        1. Checks if the file even exists
        2. Attempts to open the file for reading. This will determine if the file has a write lock.
            Write locks occur when the file is being edited or copied to, e.g. a file copy destination
        3. Attempts to rename the file. If this fails the file is open by some other process for reading. The 
            file can be read, but not written to or deleted.
    @param filePath:
    '''
    if not (os.path.exists(filePath)):
        return False
    try:
        f = open(filePath, 'r')
        f.close()
    except IOError:
        return True

    lockFile = filePath + ".lckchk"
    if (os.path.exists(lockFile)):
        os.remove(lockFile)
    try:
        os.rename(filePath, lockFile)
        sleep(1)
        os.rename(lockFile, filePath)
        return False
    except WindowsError:
        return True
