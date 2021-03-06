import os
import sys
fileList = []
rootdir = sys.argv[1]
for root, subFolders, files in os.walk(rootdir):
    for file in files:
        fileList.append(os.path.join(root,file))
print fileList

#================================================================================
# List of all the files, total count of files and folders & Total size of files.
#================================================================================
import os
import sys

fileList = []
fileSize = 0
folderCount = 0
rootdir = sys.argv[1]

for root, subFolders, files in os.walk(rootdir):
    folderCount += len(subFolders)
    for file in files:
        f = os.path.join(root,file)
        fileSize = fileSize + os.path.getsize(f)
        #print(f)
        fileList.append(f)

print("Total Size is {0} bytes".format(fileSize))
print("Total Files", len(fileList))
print("Total Folders", folderCount) 
