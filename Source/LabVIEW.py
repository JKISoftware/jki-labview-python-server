#########################################################################
#
# Custom LabVIEW TCP Server Client Script for Python 2.x and 3.x
#
# Copyright (c) 2003-2010 JKI. All rights reserved.
#
# Author: Jim Kring [jim.kring@jameskring.com]
# Author: Philippe Guerit [philippe.guerit@jameskring.com]
#
# This library is provided "AS IS" ,WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.
#
# James Kring, Inc. -- http://www.jameskring.com
#
#########################################################################

import socket as _socket
import sys

# get python major version as integer
from sys import version as pythonVersion
pythonVersionMajor = int(pythonVersion[0])

_serverHost = 'localhost'
_serverPort = 50007
isConnected = 0
_sockobj = None
_error_string = "error:"

def getAppVersion():
    'get RAFL executable version as major.minor.bugfix.build# (returns "0.0.0.0" when calling RAFL IDE)'

    # if already connected, disconnect first and then reconnect.
    if isConnected:
        return _passCommand("System.GetAppVersion")
    else:
        print "not connected. Run connect method first"            

def connect():
    'opens a connection to LabVIEW Server'
    global _sockobj, isConnected

    # if already connected, disconnect first and then reconnect.
    if isConnected:
        disconnect()

    _sockobj = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)      # create socket
    _sockobj.connect((_serverHost, _serverPort))   # connect to LV

    _instrumentList = _passCommand("System.GetInstruments()")

    for _instrument in _instrumentList:
        _instrumentName = _instrument[0]
        _instrumentFunctionList = _instrument[1]
        _execString = _instrumentName + ' = _Instrument(' + repr(_instrumentName) + ", " + repr(_instrumentFunctionList) +')'
        exec _execString in globals() # execute in global (module's) scope, not function's scope

    isConnected = 1


def disconnect():
    'closes the connection to LabVIEW Server'
    global isConnected
    _sockobj.close()                             # close socket
    isConnected = 0

# Add a recv_all function PJM 3-26-2010 (not tested on python 3.0, but on python 2.6.4)
def recv_all(my_socket, pack_size=8):
    'this routine is supposed to receive all data in the socket buffer in chunks using a prefixed size (of pack_size which default to 8)'
    #data length is packed into pack_size bytes
    total_len=0;total_data=[];size=sys.maxint;
    data=size_data=sock_data=chunk_data='';recv_size=8192
    while total_len<size:                                   #while we have not received all data
        sock_data=my_socket.recv(recv_size)                 #Get recv_size amount of data
        if not total_data:                                  #if total_data list is empty
            if len(sock_data)>pack_size:                    #if size of received data is greater than pack_size
                size_data+=sock_data                        #size_data=size_data + received data
                chunk_data=size_data[:pack_size]
                # python 3 requires data to be decoded
                if (pythonVersionMajor >= 3):
                    chunk_data = bytes.decode(chunk_data)
                size=int(chunk_data)                        #convert the first pack_size byte to an integer the first pack_size byte (<- this is how much data we have to get)
                recv_size=size                              #set recv_size with size
                if recv_size>524288:recv_size=524288        #coerce recv_size to be no greater than 512 KB
                total_data.append(size_data[pack_size:])    #append to the total data list the string after the pack_size first byte
            else:                                           #if size of received data is NOT greater than pack_size
                size_data+=sock_data                        #size_data=size_data + received data
        else:                                               #if total_data list is NOT empty then append what we just received to it
            total_data.append(sock_data)                    #append to total_data what was just received
        total_len=sum([len(i) for i in total_data ])        #Compute total_len
    # python 3 requires data to be decoded
    if (pythonVersionMajor >= 3):
         data = bytes.decode(''.join(total_data))
    else:
         data = ''.join(total_data)
    return data                                             #Return the received string

def _passCommand(command):
    'passes a command to LabVIEW Server'

##    global lvdata
## We prepend the command length (8 char long) to the message and send it to LV --PJM 6-16-06
    # Compute message length and pad with 0 on the left if required
    commandSize=str(len(command)).rjust(8,'0')
    # Prepend msg size to msg
    completeCommand=commandSize+command
    # python 3 requires data to be encoded
    if (pythonVersionMajor >= 3):
        completeCommand = str.encode(completeCommand)
    # Send complete command
    _sockobj.sendall(completeCommand)   #Note: sendall can only be used if the socket is in blocking mode (which is the default mode)
#    data = _sockobj.recv(11565536)
    data = recv_all (_sockobj,8)        #We expect the return msg to have an header with size information 8 char long
    # python 3 requires data to be decoded
    if (pythonVersionMajor >= 3):
        data = bytes.decode(data)
    #search for an error in the response string
    if data.rfind(_error_string) == 0:
        error = True
        data = data[len(_error_string):] # get data after "error:" string
    else:
        error = False
    #convert data from string to python data
##    #test for performance improvement inconclusive
##    if data == "None":
##        lvdata = None
##    else:
##        execString = "lvdata = " + data
##        exec(execString, globals())
    execString = "lvdata = " + data
    exec(execString, globals())
    #return lvdata or raise an error
    if error:
        raise LabVIEWError(lvdata)
    else:
        return lvdata


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class LabVIEWError(Error):
    """Exception raised for errors generated in LabVIEW.

    Attributes:
        code -- LabVIEW Error Code
        source -- location of the error
        message -- explanation of the error
    """

    def __init__(self, error):
        self.code = error[0]
        self.source = error[1]
        self.message = error[2]

    def __str__(self):
##        return "%s" % (self.message,)
        # Change to return more than just the message.
        return "Error code: %d.\nError source: %s.\nMessage: %s\n" % ( self.code, self.source, self.message )


class _Instrument:

    def __init__(self, _instrumentName, _functionNames):

        for _functionName in _functionNames:
            _execString = "self." + _functionName + " =_Function('" + _instrumentName + "." + _functionName + "')"
            exec(_execString)


class _Function:

    def __init__(self, name):

        self._name = name

    def __call__(self, a = None):

        if isConnected:

            if (a == None):

                return _passCommand(self._name + '()')

            else:

                return _passCommand(self._name + '(' + repr(a) + ')')

        else: print('Not Connected: Run "%s.connect()" method to connect.'% __name__)

