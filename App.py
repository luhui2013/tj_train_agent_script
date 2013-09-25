#!/usr/bin/python
'''
Created on Jun 26, 2013

@author: luhui
'''


import SocketServer
import time 
import os,sys

HOST='0.0.0.0'
PORT=2013
ADDR=(HOST,PORT)

USEAGE='''
   ===========================useage==================
   help
       show help info
   quit
       exit this connection
   reboot
       reboot pc
   setnetworkconfig -address ADDRESS -netmask NETMASK -gateway GATEWAY
   shownetworkconfig
   
   setdatetime DATETIME
   showdatetime
   ===========================useage end==================
'''

IP_CONFIG_FILE_TML='''
auto lo
iface lo inet loopback


auto eth0
iface eth0 inet static
address %s
netmask %s
gateway %s  
'''
IP_CONFIG_FILE='/etc/network/interfaces'
#IP_CONFIG_FILE='/home/luhui/interfaces'
IP_CONFIG_ARGS_ITEM=('-address','-netmask','-gateway')


def now():
    return time.ctime(time.time())


class MyRequestHandler(SocketServer.StreamRequestHandler):  
                
    def handle(self):
        print '...connected from:',self.client_address
        self.show_info(USEAGE)
        
        while True:
            data=self.rfile.readline().strip()
            if len(data)==0:
                continue
            
            
            cmd_list=data.split()
            cmd=cmd_list[0].strip()
            if cmd=='help':
                self.show_info(USEAGE)
            elif cmd=='quit':
                self.show_info('Bye')
                #time.sleep(3)
                break;
            elif cmd=='reboot':
                if os.system('reboot')!=0:
                    self.show_info('reboot failed!')
                
            elif cmd=='setnetworkconfig':
                if len(cmd_list)>1:
                    args=self.process_args(cmd_list[1:])
                    if len(args)==3:
                        result=self.write_ip_config(args)
                        if result:
                            self.show_info('setnetworkconfig success!')
                    else:
                        self.show_info(USEAGE)
                else:
                    self.show_info(USEAGE)
            elif cmd=='shownetworkconfig':
                self.show_ip_config()
            elif cmd=="showdatetime":
                self.show_info(now())
            elif cmd=="setdatetime":
                if len(cmd_list)>1:
                    result=True
                    if os.system("date -s \"%s\"" % " ".join(cmd_list[1:]))!=0:
                        result=False
                    if result and os.system('hwclock -w')!=0:
                        result=False
                    if not result:
                        self.show_info('setdatetime failed!')
                    else:
                        self.show_info('setdatetime success,now is %s!' % now())
                        
                        
                else:
                    self.show_info(USEAGE)
            else:
                self.show_info(USEAGE)
        
        self.connection.close()
        
    
    def process_args(self,arg_list):
        result={}
        args_max_len=6
        
        if len(arg_list)!=args_max_len: return {}
        
        for item in IP_CONFIG_ARGS_ITEM:
            for i in range(args_max_len):
                arg=arg_list[i]
                if arg==item and i+1<args_max_len and (arg_list[i+1] not in IP_CONFIG_ARGS_ITEM):
                    if not result.has_key(item):
                        result[item]=arg_list[i+1]
                
        
        return result
        
        
    def show_ip_config(self):
        lines=None
        
        file_exist,info=self.check_ip_config_file()
        if(not file_exist):
            self.show_info(info)
            return
        
        file=None
        try:
            f=open(IP_CONFIG_FILE,'r')
            lines=f.readlines()
        finally:
            if file!=None:
                file.close()
        
        if lines!=None:
            self.show_info("network config file: %s " % IP_CONFIG_FILE)
            self.show_info("-------------------------------------------------")
            for line in lines:
                self.show_info(line)
        else:
            self.show_info('read network config file error!')
        
        
    def write_ip_config(self,args):
        result=False
        tml=IP_CONFIG_FILE_TML % (args[IP_CONFIG_ARGS_ITEM[0]],args[IP_CONFIG_ARGS_ITEM[1]],args[IP_CONFIG_ARGS_ITEM[2]])
        
        file_exist,info=self.check_ip_config_file()
        if(not file_exist):
            self.show_info(info)
            return False
        
        file=None
        try:
            f=open(IP_CONFIG_FILE,'w')
            f.write(tml)
            result=True
        finally:
            if file!=None:
                file.close()
        
        return result
        
        
    
    def check_ip_config_file(self):
        if not os.path.exists(IP_CONFIG_FILE): return False,'network config file not found!'
        return True,''

    def show_info(self,msg):
        msg="%s %s" % (msg,os.linesep)
        self.wfile.write(msg)   

    

tcpServ=SocketServer.ThreadingTCPServer(ADDR,MyRequestHandler)
print 'waiting for connection...'
tcpServ.serve_forever()
