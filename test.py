import os

name = 'fred'
host = 'imperian.com'
port = 23
encoding = 'ascii'
executable_path = os.path.join('c:\\', 'testclient.py')
print(executable_path)
print(os.path.exists(executable_path))