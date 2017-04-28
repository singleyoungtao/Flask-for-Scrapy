#!/bin/python3
#-*-coding:utf-8-*-

# import os

# def f():
#     return 5

# def z():
#     a = f()
#     return a

# print(z())

import requests

cs_url = 'http://localhost:6800/daemonstatus.json'
r = requests.get(cs_url)
print(r.content)
print(r.headers)

# cs_url2 = 'http://localhost:6800/schedule.json'
# # r2 = requests.post(cs_url2, "project=nwsuaf&&spider=nwsuaf")
# # 这个方法出错了
# r2 = requests.post(cs_url2, {'project':'nwsuaf','spider':'nwsuaf'})
# print(r2.content)
# i = 10
# while i>3 :
#     i = i-1
#     print(i)