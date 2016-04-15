# coding: utf-8

#!/opt/SkypeDevil/bin/python
# Walker 2016 01

import time
import sys
import ConfigParser
import logging

from nsnitro import *



config = ConfigParser.ConfigParser()
#config.read('config.ini')

config.read('/opt/SkypeDevil/config.ini')

ip = config.get('Login', 'ip')
user = config.get('Login', 'user')
passwd = config.get('Login', 'passwd')

# login and return nitro obj
def ns_login(ip, user, passwd):
    nitro = NSNitro(ip, user, passwd)
    try:
        nitro.login()
        return nitro
    except:
        print sys.exc_info()

        
        
# read load balance vitual server list pair from config.ini
# return dictionary format
def read_lbvserver(lbvserver):
    lb_list = {}
    for item in config.items(lbvserver):
        # split string to list
        svr_list = item[1].split(',')
        
        # add config pair to dictionary
        lb_list[item[0]] = svr_list
    # return sever config pair dictionary
    return lb_list
    

    
# read all available service of each lb virtual server from config.ini
def read_all_lb_service_pair(available_service):
    av_svc = {}
    for item in config.items(available_service):
        svc_list = item[1].split(",")
        #logging.info('svc_list: %s' % str(svc_list))
        
        # add "lbvserver: services" pair to dictionary
        av_svc[item[0]] = svc_list
        
    
    # return lbvserver: available service pair dictionary
    return av_svc
    


# search the lbvsvr name match from config.ini
def search_lbvsvr_name(lbvsvr_group, lbvsvr_name):
    av_svc_dic = read_all_lb_service_pair(lbvsvr_group)
    
    match_list = []
    match_dic = {}
    
    # loop the keys
    for key in av_svc_dic.keys():
        logging.info("key: %s" % key)
        
        # the key match lbvsvr_name
        if lbvsvr_name in key:
            match_list.append(key)
    
    # set the matched key:value to dictionary
    for i in match_list:
        match_dic[i] = av_svc_dic[i]
    
    # return the dictoionary of matched lbvsvr and services
    return match_dic
    

    
    
    
# get server status
def get_sever_status(nitro_obj, server_name):
    server = NSServer()
    server.set_name(server_name)
    try:
        server = server.get(nitro_obj, server)
        print server.get_name() + ": " + server.get_state()
    except:
        print sys.exc_info()
        
        
        
# get service from load balance virtual server 
def get_lbvserver_service(nitro_obj, lbsvr_name):
    lbbinding = NSLBVServerServiceBinding()
    lbbinding.set_name(lbsvr_name)
    
    lbb_list = []
    try:
        lbbindings = NSLBVServerServiceBinding.get(nitro_obj, lbbinding)
        
        # print service name
        for lbb in lbbindings:
            #print "sgn: " + lbb.get_servicename()
            #return lbb.get_servicename()
            lbb_list.append(lbb.get_servicename())
    except:
        #print sys.exc_info()
        logging.info("except: %s" % sys.exc_info())

    return lbb_list
        


# add service to load balance virtual server
def add_lbvserver_service(lbsvr_name, service_name):
    nitro = ns_login(ip, user, passwd)
    
    #logging.info("add_lbvserver_service: opts type {0} {1}".format(type(lbsvr_name), type(service_name)))
    
    # bind service to lbvserver test
    lbbinding = NSLBVServerServiceBinding()
    lbbinding.set_name(lbsvr_name)
    lbbinding.set_servicename(service_name)
    lbbinding.set_weight(1)
    
    try:
        NSLBVServerServiceBinding.add(nitro, lbbinding)
        #print "Binding: added %s to %s" % (service_name, lbsvr_name)
        logging.info("Binding: added {0} to {1}".format(service_name, lbsvr_name))
    except:
        #print sys.exc_info()
        logging.info("except: {}".format(sys.exc_info()))
        


# delete service from load balance virtual server  
def del_lbvserver_service(lbsvr_name, service_name):
    nitro = ns_login(ip, user, passwd)

    # delete binding test
    lbbinding = NSLBVServerServiceBinding()
    lbbinding.set_name(lbsvr_name)
    lbbinding.set_servicename(service_name)
    
    try:
        NSLBVServerServiceBinding.delete(nitro, lbbinding)
        #print "Unbinding: del %s to %s" % (service_name, lbsvr_name)
        logging.info("Unbinding: del {0} from {1}".format(service_name, lbsvr_name))
    except:
        #print sys.exc_info()
        logging.info("except: %s" % sys.exc_info())




def get_lbvserver_info(svr_group):
    
    nitro = ns_login(ip, user, passwd)
    #logger.debug("%s %s %s" % (ip, user, svr_group))
    
    
    betasvr = read_lbvserver(svr_group)
    out ={}
    
    for key in betasvr:
        # more than 1 service bind
        if len(betasvr[key]) > 1:
            j = 0 
            
            # loop the virtual server name
            for i in betasvr[key]:
                if j == 0:
                    out[key] = get_lbvserver_service(nitro, i)
                    j = 1
                else:
                    # multiple service in a virtual server, merge the list
                    out[key] += get_lbvserver_service(nitro, i)
                
        # just 1 service bind        
        else:
            out[key] = get_lbvserver_service(nitro, betasvr[key][0])
            
    return out


