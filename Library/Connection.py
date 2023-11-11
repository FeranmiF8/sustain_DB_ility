import argparse
import socket
import threading
from time import sleep
import random
from table import *
import json


## Provides an abstraction for the network layer
class Connection:

    # class variables
    sock = None
    conn = None
    ip = ''
    user = ''
    password = ''
    tables = []


    '''
    constructor for Connection object
    @param ip: IP address of the server
    @param user: username for authentication
    @param password: password for authentication
    '''
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password

    
    '''
    Connect to the server
    '''
    def connect(self):
        print('connecting')
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('socket created', self.ip)
        self.conn.connect((self.ip, 12000))
        print('connected')

        # start the thread to receive data on the connection
        # self.collect_thread = threading.Thread(name="Collector", target=self.collect)
        # self.stop = False
        # self.collect_thread.start()

    '''
    Disconnect from the server
    '''
    def disconnect(self):
        self.conn.close()

    '''
    Destructor for Connection object
    '''
    def __del__(self):
        if self.sock is not None:
            self.sock.close()
        if self.conn is not None:
            self.conn.close()

    '''
    Get table data from the server
    @param key: name of the table
    @return: table object
    '''
    def get(self, key):
        self.connect()
        table = None
        for i in self.tables:
            if i.name == key:
                table = i
                break
        if table is None:
            table = Table(key, [], self)
        json_obj = {
            "method": "get",
            "username": self.user,
            "accountkey": self.password,
            "tableName": key,
            "data": ""
        }

        req = json.dumps(json_obj)
        self.conn.sendall(req.encode())
        rec = self.conn.recv(1024).decode()
        data = []
        while rec != 'done':
            print(rec)
            rec = json.loads(rec)
            data.append([rec['key'], rec['data']])
            rec = self.conn.recv(1024).decode()
        print('datifa:',data)
        
        newTable = Table(key, data, self)
        self.tables.append(newTable)
        self.__del__()
        return  newTable


    '''
    Set table data to the server
    @param table: table object
    '''
    def setTable(self, table):
        for i in self.tables:
            if i.name == table.name:
                i = table
                break
        if table not in self.tables:
            self.tables.append(table)
        self.connect()
        json_obj = {
            "method": "set",
            "username": self.user,
            "accountkey": self.password,
            "tableName": table.name,
            "data": ''
        }
        
        data = {'key':[], 'data':[]}
        
        for i in table.data:
            data['key'].append(i[0])
            data['data'].append(i[1])
        
        # print('DATA:',data)
            
        json_obj['data'] = data

        req = json.dumps(json_obj)
        self.conn.sendall(req.encode())
        self.__del__()
        
    def test(self, msg):
        self.connect()
        self.conn.sendall(msg.encode())
        self.disconnect()
        # print('worked')
        
    def closeRemote(self):
        json_obj = {
            "method": "quit",
            "username": self.user,
            "accountkey": self.password,
            "tableName": '',
            "data": ''
        }
        req = json.dumps(json_obj)
        self.conn.sendall(req.encode())
        


