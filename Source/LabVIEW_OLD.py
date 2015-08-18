#########################################################################
# 
# Custom LabVIEW TCP Server Client Script
# 
# Copyright (c) 2003-2009 JKI. All rights reserved.
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

_serverHost = 'localhost'
_serverPort = 50007
isConnected = 0
_sockobj = None
_error_string = "error:"


def connect():
    'opens a connection to LabVIEW Server'
    global _sockobj, isConnected
    _sockobj = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)      # create socket
    _sockobj.connect((_serverHost, _serverPort))   # connect to LV
    isConnected = 1


def disconnect():
    'closes the connection to LabVIEW Server'
    global isConnected
    _sockobj.close()                             # close socket
    isConnected = 0
    

def _passCommand(command):
    'passes a command to LabVIEW Server'

## We prepend the command length (8 char long) to the message and send it to LV --PJM 6-16-06
    # Compute message length and pad with 0 on the left if required
    commandSize=str(len(command)).rjust(8,'0')
    # Prepend msg size to msg
    completeCommand=commandSize+command
    # Send complete command
    _sockobj.send(completeCommand)
    data = _sockobj.recv(11565536)
    if data.rfind(_error_string) == 0:
        error = True
        data = data[len(_error_string):] # get data after "error:" string
    else:
        error = False
    execString = "lvdata = " + data
    exec execString
    if error:
        raise _LabVIEWError(lvdata)
    else:
        return lvdata


class _Error(Exception):
    """Base class for exceptions in this module."""
    pass


class _LabVIEWError(_Error):
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
    	return "%s" % (self.message,)


class _Instrument:
    
    def __init__(self, _instrumentName, _functionNames):
        
        for _functionName in _functionNames:
            _execString = "self." + _functionName + " =_Function('" + _instrumentName + "." + _functionName + "')"
            exec _execString


class _Function:
    
    def __init__(self, name):

        self._name = name

    def __call__(self, a = None):

        if isConnected:        
        
            if (a == None):
            
                return _passCommand(self._name + '()')
        
            else:
            
                return _passCommand(self._name + '(' + `a` + ')')

        else: print 'Not Connected: Run "%s.connect()" method to connect.'% __name__


connect()

_instrumentList = _passCommand("System.GetInstruments()")

for _instrument in _instrumentList:
    _instrumentName = _instrument[0]
    _instrumentFunctionList = _instrument[1]
    _execString = _instrumentName + ' = _Instrument(' + `_instrumentName` + ", " + `_instrumentFunctionList` +')'
    exec _execString
     

disconnect()