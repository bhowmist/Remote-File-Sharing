#!/usr/bin/python
# File sharing using RPyC
# Client code
# Paul Talaga - paul.talaga@uc.edu
# Jan, 2015

import rpyc, os, sys

# Reads a file on the local filesystem and returns a tuple
def getFile(filename):
  if '../' in filename:
    return (False,"../ can not be part of the filename")
  print "Someone is getting " + filename
  try:
    f = open(source + '/' + filename, 'rb')
    data = f.read()
    f.close()
    # First element in tuple is success flag
    return (True, data)
  except:
    return (False,filename + " doesn't exist")

# Retrieve list of files in the shared folder
def getFiles():
  return  os.listdir(source)

if __name__ == "__main__":
  
  if len(sys.argv) < 3:
    print "./client.py <shared folder>  <destination folder> <server (will use localhost if not given)>"
    sys.exit()

  source = sys.argv[1]
  # todo: verify source is folder
  dest = sys.argv[2]
  # todo: verify dest is folder
  # By default use localhost for server
  server = 'localhost'
  if len(sys.argv) == 4:
    server = sys.argv[3]

  c = rpyc.connect(server, 18861)

  bgsrv = rpyc.BgServingThread(c) # Fire up background thread to listen for RPyC requests

  # Sends both file functions to server
  c.root.setCallbacks(getFiles,getFile)
  
  print "Enter 'q' for quit, 'ls' for file list, or # to download"

  key_in = ' '
  while key_in != 'q':
    key_in = raw_input()
    if key_in == 'ls':
      print c.root.getFileList()
    elif key_in == 'q':
      break
    elif key_in.isdigit():  # We assume files are reference by numbers
      # This gets a success flag, file name, and filedownloader function
      (succ, fname, fhandle) = c.root.getFileDownloader(key_in)
      if succ == True:
        try:
          (fsucc, data) = fhandle(fname)  # Get the file contents!
          if fsucc == False:
            print "Download Error: " + data
            continue
          f = open(dest +'/' + fname, 'wb')
          f.write(data)
          print "Successfully got " + fname
          f.close()
        except:
          print "Error: Callback error"
      else:
        print "Error: " + str((succ, fname))
    else:
      print "Error: " + key_in + " not a command."


  bgsrv.stop()
  c.close()
