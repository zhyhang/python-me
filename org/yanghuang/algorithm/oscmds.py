# coding=UTF-8

import  os

print(os.getcwd())
cpath=os.path.join(os.getcwd(),'tmp')
print(cpath)
print(os.sep)
print(os.path.exists(cpath))
print(os.curdir)