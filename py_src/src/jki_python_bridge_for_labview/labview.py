#########################################################################
#
# JKI Python Bridge for LabVIEW
# Client Script for Python 3.6-3.10
#
# Copyright (c) 2003-2022 JKI. All rights reserved.
#
# Visit http://jki.net/python-bridge for updates
#
#########################################################################

import ast
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
    'get executable version as major.minor.bugfix.build# (returns "0.0.0.0" when calling RAFL IDE)'

    # if already connected, disconnect first and then reconnect.
    if isConnected:
        return _passCommand("System.GetAppVersion")
    else:
        print("not connected. Run connect method first")


def connect(serverHost='localhost', serverPort=50007):
    'opens a connection to LabVIEW Server'
    global _sockobj, isConnected
    _serverHost = serverHost
    _serverPort = serverPort
    # if already connected, disconnect first and then reconnect.
    if isConnected:
        disconnect()

    _sockobj = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)  # create socket
    _sockobj.connect((_serverHost, _serverPort))  # connect to LV

    _instrumentList = _passCommand("System.GetInstruments()")

    for _instrument in _instrumentList:
        # print _instrument
        _instrumentName = _instrument[0]
        _instrumentFunctionList = _instrument[1]
        # _instrumentArgumentsList = _instrument[2]
        # print _instrumentFunctionList
        _execString = _instrumentName + ' = _Instrument(' + repr(_instrumentName) + ", " + repr(
            _instrumentFunctionList) + ')'
        exec(_execString, globals())  # execute in global (module's) scope, not function's scope

    isConnected = 1


def disconnect():
    'closes the connection to LabVIEW Server'
    global isConnected
    _sockobj.close()  # close socket
    isConnected = 0


def recv_all(my_socket, pack_size=8):
    'this routine is supposed to receive all data in the socket buffer in chunks using a prefixed size (of pack_size which default to 8)'
    # data length is packed into pack_size bytes
    total_len = 0
    total_data = []
    size = sys.maxsize
    if pythonVersionMajor>=3:
        data = size_data = sock_data = chunk_data = bytes()
    else:
        data = size_data = sock_data = chunk_data = ''

    recv_size = 8192
    while total_len < size:  # while we have not received all data
        sock_data = my_socket.recv(recv_size)  # Get recv_size amount of data
        if not total_data:  # if total_data list is empty
            if len(sock_data) > pack_size:  # if size of received data is greater than pack_size
                size_data += sock_data  # size_data=size_data + received data
                chunk_data = size_data[:pack_size]
                # python 3 requires data to be decoded
                if (pythonVersionMajor >= 3):
                    chunk_data = bytes.decode(chunk_data)
                size = int(
                    chunk_data)  # convert the first pack_size byte to an integer the first pack_size byte (<- this is how much data we have to get)
                recv_size = size  # set recv_size with size
                if recv_size > 524288: recv_size = 524288  # coerce recv_size to be no greater than 512 KB
                total_data.append(
                    size_data[pack_size:])  # append to the total data list the string after the pack_size first byte
            else:  # if size of received data is NOT greater than pack_size
                size_data += sock_data  # size_data=size_data + received data
        else:  # if total_data list is NOT empty then append what we just received to it
            total_data.append(sock_data)  # append to total_data what was just received
        total_len = sum([len(i) for i in total_data])  # Compute total_len
    # python 3 requires data to be decoded
    if (pythonVersionMajor >= 3):
        # data = bytes.decode(''.join(total_data))
        data = b''.join(total_data).decode()
    else:
        data = ''.join(total_data)
    return data  # Return the received string


def _passCommand(command):
    'passes a command to LabVIEW Server'

    ## We prepend the command length (8 char long) to the message and send it to LV --PJM 6-16-06
    # Compute message length and pad with 0 on the left if required
    commandSize = str(len(command)).rjust(8, '0')
    # Prepend msg size to msg
    completeCommand = commandSize + command
    # python 3 requires data to be encoded
    if (pythonVersionMajor >= 3):
        completeCommand = str.encode(completeCommand)
    # Send complete command
    _sockobj.sendall(
        completeCommand)  # Note: sendall can only be used if the socket is in blocking mode (which is the default mode)
    #    data = _sockobj.recv(11565536)
    data = recv_all(_sockobj, 8)  # We expect the return msg to have an header with size information 8 char long
    # python 3 requires data to be decoded
    # if (pythonVersionMajor >= 3):
    #     data = bytes.decode(data)
    # search for an error in the response string
    if data.rfind(_error_string) == 0:
        error = True
        data = data[len(_error_string):]  # get data after "error:" string
    else:
        error = False
    # convert data from string to python data

    # execString = "lvdata = " + data
    # exec(execString, globals())

    lvdata = ast.literal_eval(data)

    # return lvdata or raise an error
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
        return "Error code: %d.\nError source: %s.\nMessage: %s\n" % (self.code, self.source, self.message)


# function that allows to script a child of the _Function class with a specific name and set of parameters
def _scriptFuncClass(functionName, _argumentsList, _documentation):
    """returns a string that can be executed by python to create a child of _Function"""
    _argStr = ""
    _argSize = len(_argumentsList)
    _argCount = 0
    for _argument in _argumentsList:
        _argStr = _argStr + _argument
        _argCount = _argCount + 1
        if _argCount < _argSize:
            _argStr = _argStr + ","
    if _argCount > 0:
        _commaStr = ","
    else:
        _commaStr = ""

    _strStub = '''class _Function''' + functionName + '''(_Function):
    def __call__(self''' + _commaStr + _argStr + ")" + ''':
        """''' + _documentation + ''' """
        return self._executeFunction(''' + _argStr + ''')'''
    return _strStub


class _Instrument:
    def __init__(self, _instrumentName, _functionClusters):
        self.name = _instrumentName

        for _functionCluster in _functionClusters:
            _functionName = _functionCluster[0]
            _functionArgList = _functionCluster[1]
            _functionDoc = _functionCluster[2]
            _funExecStr = _scriptFuncClass(_functionName, _functionArgList, _functionDoc)
            exec(_funExecStr)
            _execString = '''self.''' + _functionName + ''' =_Function''' + _functionName + "('" + _instrumentName + '''.''' + _functionName + '''' ,''' + repr(
                _functionArgList) + ''')'''
            exec(_execString)


class _Function:
    # myArgs = None
    def __init__(self, name, *args):
        self._name = name
        self.argsNames = list(args)

    def _executeFunction(self, *args):
        a = list(args)
        if isConnected:

            if (a == None):

                return _passCommand(self._name + '()')

            else:

                return _passCommand(self._name + '(' + repr(a) + ')')

        else:
            print(('Not Connected: Run "%s.connect()" method to connect.' % __name__))
