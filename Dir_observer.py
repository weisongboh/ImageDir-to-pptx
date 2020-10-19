import sys
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.utils import dirsnapshot as dirsnap
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from pathlib import Path
from Evos_import import ProcessImageFolder

watchpath = 'C:\\Image\\directory' #define directory to watch

global mod_count_global
mod_count_global = {}

class ActionOnEvent(FileSystemEventHandler):
    def __init__(self):
        self.mod_count = 0

    def getmodcount(self):
        return self.mod_count

    def empty_count(self):
        self.mod_count = 0
        return True

    def patternMatch(self,path):
        if 'Expt' in path:
            return True
        else:
            return False
    def isImage(self,path):
        attributes = ['.tif','.jpg']
        for attribute in attributes:
            if attribute in path:
                return True
        return False

    def on_created(self, event):
        global mod_count_global
        self.mod_count += 1 #increase file count by 1 for every count

        if event.is_directory:
            if self.patternMatch(event.src_path):
                print('Experiment Folder detected')
            elif 'New folder' in event.src_path:
                print('User created new folder')
            else:
                #Add folder to global memory
                print('Normal Folder Detected')
                mod_count_global[event.src_path]= 0
        else:
            filepath = Path(event.src_path)
            fp_string = str(filepath.parent)
            filestr = str(filepath)
            #increase count if folder is image folder
            if (fp_string in mod_count_global) and self.isImage(filestr):
                mod_count_global[fp_string] += 1


        return None
    def on_modified(self, event):
        if event.is_directory:
            if self.patternMatch(event.src_path):
                print('Experiment Folder detected')
            elif 'New folder' in event.src_path:
                print('User created new folder')
            else:
                #Check if modified folder exists
                if event.src_path in mod_count_global:
                    return None
                else:
                    # Add folder to global memory
                    print('Normal Folder Detected')
                    mod_count_global[event.src_path] = 0
        return None
class myThread(threading.Thread): #example thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        print_time(self.name, 5, self.counter)
        print("Exiting " + self.name)


class Sentinel(threading.Thread):
    def __init__(self, threadID: object, name: object, counter: object) -> object:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        path = watchpath
        fooaction = ActionOnEvent()
        eventhandler = LoggingEventHandler()
        observer = Observer()
        observer.schedule(fooaction, path, recursive=True)
        observer.schedule(eventhandler,path,recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


class SentinelCounter(threading.Thread):
    def __init__(self, threadID, name, counter={}):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def get_memory(self):
        return self.counter

    def run(self):
        try:
            mem_dict = self.get_memory()
            while True:
                # mem_dict = [directory]: [filecount, no. of cycles without increment in filecount]
                if mod_count_global:
                    for folder in mod_count_global:
                        if folder in mem_dict:
                            folder_entry = mem_dict[folder]

                            if folder_entry[1] >= 3 and folder_entry[0] == 0: #Check if filecount has not increased for no. of cycles

                                result = mem_dict.pop(folder)
                                result2 = mod_count_global.pop(folder)
                                print(result, result2)
                                break
                            elif folder_entry[1] >= 3 and folder_entry[0] != 0:
                                ProcessImageFolder(folder)
                                result = mem_dict.pop(folder)
                                result2 = mod_count_global.pop(folder)
                                print(result, result2)
                                break
                            elif folder_entry[0] == mod_count_global[folder]:
                                #increase stagnant count cycle by 1
                                folder_entry[1] += 1
                            else:
                                folder_entry[0] = mod_count_global[folder]
                                folder_entry[1] = 0
                                print('filecount is still increasing')
                        else:
                            #create new entry for new directory
                            mem_dict[folder] = [mod_count_global[folder],0]

                #print(mod_count_global)
                time.sleep(5)
        except:
            print(mod_count_global)
            print('failed to read global variable')
            raise
        return None


def print_time(threadName, counter, delay):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


# Create new threads
thread1 = Sentinel(1, 'sentinel', 1)
thread3 = SentinelCounter(3, 'Observer Count')

# Start new Threads
thread1.start()
thread3.start()
