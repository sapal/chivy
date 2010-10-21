# coding=utf-8
import socket

def getIpAddress():
    return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][0]

def getIpAddresses():
    return  socket.gethostbyname_ex(socket.gethostname())[2]

