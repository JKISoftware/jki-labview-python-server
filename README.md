# JKI Python Bridge for LabVIEW

Easily add a Python API to your LabVIEW application.

[![LabVIEW](https://img.shields.io/badge/LabVIEW-2020-%23E37725.svg?)](https://www.ni.com/en-us/shop/labview/select-edition/labview-community-edition.html)
[![versions](https://img.shields.io/pypi/pyversions/jki-python-bridge-for-labview.svg)](https://github.com/JKISoftware/jki-labview-python-server)
[![License](https://img.shields.io/badge/License-BSD%2bPatent-blue.svg)](https://opensource.org/license/bsdpluspatent) 
[![Image](https://www.vipm.io/package/jki_lib_python_bridge_for_labview/badge.svg?metric=installs)](https://www.vipm.io/package/jki_lib_python_bridge_for_labview/) [![Image](https://www.vipm.io/package/jki_lib_python_bridge_for_labview/badge.svg?metric=stars)](https://www.vipm.io/package/jki_lib_python_bridge_for_labview/)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

## Getting Started

- [Install LabVIEW Package with VIPM](https://www.vipm.io/package/jki_lib_python_bridge_for_labview/) (You'll use this to create your APIs)

- Install the jki-python-bridge-for-labview using `pip`

`python3 pip install jki-python-bridge-for-labview`

Note: be sure to install the same version as the LabVIEW package you installed. For example, if you've installed version 5.0.0 of the LabVIEW package, then you'd install the same version of the python package as follows:

`python3 pip install jki-python-bridge-for-labview==5.0.1`

- Open the LabVIEW Example and Run it

![image](https://user-images.githubusercontent.com/381432/197280513-60e018e6-c4ba-4255-8c43-70af6407f4ee.png)

![image](https://user-images.githubusercontent.com/381432/197280631-0c5e4a1b-b50c-40e7-b195-4ed9d41a6d4e.png)

- Open cmd.exe or powershell.exe terminal
- Create a virtual environment for testing
```
python -m venv .venv
```
- Activate it in PowerShell
```
.\.venv\scripts\activate.ps1
```
- Activate it in a Command Shell
```
.\.venv\scripts\activate.bat
```
Start Python
```
PS C:\projects\jki-labview-python-server> python
Python 3.10.4 (tags/v3.10.4:9d38120, Mar 23 2022, 23:13:41) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
```
- Interact with LabVIEW from Python

``` python
>> from jki_python_bridge_for_labview import labview as lv
>> lv.connect()
>>> lv.isConnected
1
>>> lv.example.add(1,2)
3.0
>>>
```
- Understanding what's happening
![image](https://user-images.githubusercontent.com/381432/197281397-c27abceb-d76a-40f6-932b-6f0b8e5e0b8e.png)
