#!/usr/bin/python
# File sharing using RPyC
# Server code
# Paul Talaga - paul.talaga@uc.edu
# Jan, 2015
import rpyc

class Service(rpyc.Service):
  def on_connect(self):
    pass

  def on_disconnect(self):
    print "Someone left!"
    c.getFileList() # do a scan to remove them from file lookups

  def exposed_setCallbacks(self,directory, getFile):
    c.setCallbacks(directory, getFile)

  def exposed_getFileList(self):
    return c.getFileList()

  def exposed_getFileDownloader(self, num):
    return c.getFileDownloader(num)

# We separate the RPyC service from the class so all state can be stored in the FileServer class.
class FileServer:
  def __init__(self):
    self.callbacks = []
    self.files_available = []

  def setCallbacks(self, get_file_list, get_file):
    self.callbacks = self.callbacks + [[get_file_list, get_file, True]]
    # Rather than remove an element in the list of callbacks, we just change the last
    # element in the tuple to flag an old client.

  def getFileList(self):
    listing = ""
    user_num = 0
    cnt = 0
    self.files_available = [] # A mapping from file number to usernumber/download fn
    for (get_file_list, not_important, use) in self.callbacks:
      if use:
        try:    # Wrap this in a try just in case we lost net connection
          files = get_file_list()  # Get the files from that client
        except:
          # if we had an error, remove that client
          self.callbacks[user_num][2] = False
          user_num = user_num + 1
          print "Removed client from list"
          continue
        for f in files:
            listing = listing + str(cnt) + ": " +str(f) + "\n"
            cnt = cnt + 1
            self.files_available.append((user_num,f))
      user_num = user_num + 1
    #print str(self.files_available)
    return listing

  def getFileDownloader(self, num):
    try:
      (user_num,file_name) =self.files_available[ int(num)]
      print "Downloading " + file_name
      return (True,file_name, self.callbacks[user_num][1])
    except:
      return (False, "file index error",False)

if __name__ == "__main__":
  from rpyc.utils.server import ThreadedServer
  c = FileServer()
  t = ThreadedServer(Service, port = 18861)
  t.start()
