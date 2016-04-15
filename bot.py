#!/opt/SkypeDevil/bin/python
# Walker 2016 01

import time
import ConfigParser
import logging
import re
import shlex
import optparse
import sys

import Skype4Py

from easy_nitro import *

# Read in config.ini
config = ConfigParser.ConfigParser()
config.read('/opt/SkypeDevil/config.ini')


global admin_list
global op_list


# Log setting
logging.basicConfig(level = logging.DEBUG,
    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt = '%a, %d %b %Y %H:%M:%S',
    filename = 'bot.log',
    filemode = 'a')



help_msg_op = """
Hi ! I am Walker Bot. Nice to meet you!! :)

Your role is RD.

[Command]
 sh vsvr :  show the binding services on all PRODUCTION vserver
 
 sh bvsvr : show the binding services on all Beta Test vserver
"""


help_msg_admin = """
Hi! I am Walker Bot. Nice to meet you!! :)

Your role is Admin.

[Command]
 sh vsvr :  show the binding services on all PRODUCTION load-balance vserver
 
 sh bvsvr : show the binding services on all Beta Test vserver

 ns sh -l $VSVR : show available sevice of production vserver (UNDER CONSTRUCTION)
 .....ex: ns sh -l ec
 
 ns shb -l $VSVR : show available sevice of beta vserver (UNDER CONSTRUCTION)
 .....ex: ns shb -l ec

 ns add -l $VSVR -s $SVC : add a service to a vserver (UNDER CONSTRUCTION)
 .....ex: ns add -l ec-http-new -s http-188
 
 ns del -l $VSVR -s $SVC : remove a service from vserver (UNDER CONSTRUCTION)
 .....ex: ns del -l ec-http-new -s http-188
"""


sh_vsvr_name_pair_msg = """
*********Show Load Balance vSever and Service_Name*********

Show available options you can use.

[Example]
ec-https-new: ['https-188', 'https-189', 'https-89']

Load balance virtual server : ec-https-new
Available services : https-188 / https-189 / https-89

You can use THIS as parameter for bind / ubind service

******************************************************

"""


# available ns opts
available_opts = ('sh', 'shb', 'add', 'del')


# Read user items from config.ini and return list
def user_permission(user_cfg):
    item = config.get('Permission', user_cfg)
    item_list = item.split(',')
    return item_list



def on_attach(Status):
    if Status == Skype4Py.apiAttachAvailable:
        skype.Attach()
    if Status == Skype4Py.apiAttachSuccess:
        logging.info("api attach success")



def sh_vsvr(Message, svr_group):
    #msg = Message.Body.lower()
    out = get_lbvserver_info(svr_group)

    for s in out:
        of = "[%s]: %s" % (s, ", ".join(str(x) for x in out[s]))
        logging.info("send:: %s" % of)
        send(Message, of)



def unknown_cmd(Message):
    msg = Message.Body.lower()
    of = "Sorry, I don't know \'%s\'" % msg
    logging.info("send:: %s" % of)
    send(Message, of)



def help_msg(Message, permission):
    if permission == 'admin':
        send(Message, help_msg_admin)
    elif permission == 'op':
        send(Message, help_msg_op)
    else:
        logging.info("help msg: permission unknown")


        
def show_matched_vsvc(Message, key):
    # get matched dic
    result = search_lbvsvr_name(key)
    
    if not result:
        send(Message, "Find matched vsvc")
        for i in result:
            logging.info("got matched lb services:: %s : %s " % (i, result[i]))
            send(Message, "%s : %s" % (i, result[i]))
    else:
        logging.info("Can not find %s" % key)
        send(Message, "Can not find %s" % key)
            

# parse command to options and args
def cmd_parse(msg):
    # cmd example:
    #   ns sh -l ec                         : show 'ec' like lbvserver 
    #   ns add -l ec-http-new -s http-188   : bind http-188 to ec-http-new
    #   ns del -l ec-http-new -s http-188   : unbind http-188 from ec-http-new
    
    parser = optparse.OptionParser()
    parser.add_option('-l', "--lbvsvr", action="store", dest="lbvsvr")
    parser.add_option('-s', "--svc", action="store", dest="svc")
    
    # parsing msg string
    (options, args) = parser.parse_args(shlex.split(msg))
    
    return options, args


# check the lbvserver opts
def check_opts(lbvsvr, svc):
    chk_key = False
    chk_value = False

    if lbvsvr in prod_key:
        chk_key = True
        
    if lbvsvr in beta_key:
        chk_key = True
    
    
    for i in prod_value:
        if svc in i:
            chk_value = True
    
    for i in beta_value:
        if svc in i:
            chk_value = True

    
    if chk_key and chk_value:
        logging.info("{0} and {1} opts is in list".format(lbvsvr, svc))
        return True
    else:
        logging.info("{0} or {1} opts is not in list".format(lbvsvr, svc))
        return False

        
    
def get_list():
    prod = read_all_lb_service_pair('AvailableService')
    beta = read_all_lb_service_pair('BetaAvailableService')
    
    prod_key = []
    beta_key = []
    
    prod_value = []
    beta_value = []
    
    
    for key in prod.keys():
        prod_key.append(key)
    
    for key in beta.keys():
        beta_key.append(key)
        
    for value in prod.values():
        prod_value.append(value)

    for value in beta.values():
        beta_value.append(value)

    return prod_key, beta_key, prod_value, beta_value



def command(Message, Status): 
    #if Status == 'SENT' or Status == 'RECEIVED':
    if Status == 'RECEIVED':
        msg = Message.Body.lower()
        #print msg
        #print "type: %s" % type(msg)
        #logging.info("get cmd: %s from %s" % (msg, Message.FromDisplayName))        
        
        # FromHandle: the skypename of the message sender
        logging.info("%s send cmd: %s" % (Message.FromHandle, msg)) 
        
        # Check user permission
        if Message.FromHandle in admin_list:
            ##############
            # admin area #
            ##############
            logging.info("%s is admin" % Message.FromHandle)
            
            
            if (msg == "h"):
                send(Message, help_msg_admin)
                
            elif (msg == "sh vsvr"):
                send(Message, "***Production VServer***")
                sh_vsvr(Message, 'ProdServer')
                send(Message, "************************")
                
            elif (msg == "sh bvsvr"):
                send(Message, "***Beta Test VServer***")
                sh_vsvr(Message, 'BetaServer')
                send(Message, "************************")
            
            # enter the opts parsing area
            else:
                opts, args = cmd_parse(msg)
                
                # netscaler command
                if args[0] == 'ns' and len(args) >= 2 and args[1] in available_opts:
                    # command: ns sh -l ec
                    # show lbvserver name and available services of the lbvserver ec 
                    if args[1] == 'sh':
                        try:
                            logging.info("ns sh get opts: %s" % opts.lbvsvr)
                            lbvsvr_dic = search_lbvsvr_name('AvailableService', str(opts.lbvsvr))
                            
                            #print lbvsvr_dic
                            
                            send(Message, sh_vsvr_name_pair_msg)
                            send(Message, "The lbvsvr match: %s" % opts.lbvsvr)
                            
                            for lb in lbvsvr_dic:
                                logging.info("%s: %s" % (lb, lbvsvr_dic[lb]))
                                send(Message, "%s: %s" % (lb, lbvsvr_dic[lb]))
                            
                            
                        except:
                            logging.info("ns sh get error: %s" % sys.exc_info())
                            
                            #print sys.exc_info()
                            
                    elif args[1] == 'shb':
                    ## TODO: hard code need to be rewrite ##
                        try:
                            logging.info("ns sh get opts: %s" % opts.lbvsvr)
                            lbvsvr_dic = search_lbvsvr_name('BetaAvailableService', str(opts.lbvsvr))
                            
                            #print lbvsvr_dic
                            
                            send(Message, sh_vsvr_name_pair_msg)
                            send(Message, "The lbvsvr match: %s" % opts.lbvsvr)
                            
                            for lb in lbvsvr_dic:
                                logging.info("%s: %s" % (lb, lbvsvr_dic[lb]))
                                send(Message, "%s: %s" % (lb, lbvsvr_dic[lb]))
                            
                            
                        except:
                            logging.info("[ns sh get error]: %s" % sys.exc_info())
                            
                            #print sys.exc_info()                        
                            
                    # command: ns add -l ec-http-new -s http-188
                    # bind service to lbvserver
                    elif args[1] == 'add' and check_opts(opts.lbvsvr, opts.svc):
                        try:
                            #logging.info("ns add get opts: %s %s" % (opts.lbvsvr, opts.svc))
                            #logging.info("ns add get opts type: %s" % type(opts.lbvsvr))
                            #logging.info("ns add get opts type: %s" % type(opts.svc))
                            
                            # add service(opts.svc) to lbvserver(opts.lbvsvr)
                            add_lbvserver_service(opts.lbvsvr, opts.svc)
                            
                        except:
                            send(Message, "[ns add get error]: {0}".format(sys.exc_info()))
                            logging.info("[ns add get error]: {0}".format(sys.exc_info()))
                            #print sys.exc_info()
                            
                        else:
                            send(Message, "[ns add success]: bind {0} to {1}".format(opts.svc, opts.lbvsvr))
                            logging.info("[ns add success]: bind {0} to {1}".format(opts.svc, opts.lbvsvr))
                    
                    # command: ns del -l ec-http-new -s http-188
                    # ubind service from lbvserver
                    elif args[1] == 'del' and check_opts(opts.lbvsvr, opts.svc):
                        try:
                            logging.info("[ns del get opts]: %s %s" % (opts.lbvsvr, opts.svc))
                            #logging.info("ns del get opts: %s" % opts.lbvsvr)
                            #logging.info("ns del get opts: %s" % opts.svc)
                            
                            del_lbvserver_service(opts.lbvsvr, opts.svc)
                            
                        except:
                            send(Message, "[ns del get error]: {0}".format(sys.exc_info()))
                            logging.info("[ns del get error]:  {0}".format(sys.exc_info()))
                            
                        else:
                            send(Message, "[ns del success]: unbind {0} from {1}".format(opts.svc, opts.lbvsvr))
                            logging.info("[ns del success]: unbind %s from %s " % (opts.svc, opts.lbvsvr))
                            
                    
                    # unavailable ns command
                    else:
                        logging.info("[Unavailable ns command]: %s" % msg)
                        send(Message, "[Unavailable ns command]: %s" % msg)
                          
                # unavailable command 
                else:
                    unknown_cmd(Message)
                    logging.info("[Unavailable cmd: %s]" % msg)
            
            
            
        elif Message.FromHandle in op_list:
            ###########
            # op area #
            ###########
            logging.info("%s is op" % Message.FromHandle)
            
            if (msg == "h"):
                send(Message, help_msg_op)
            elif (msg == "sh vsvr"):
                send(Message, "***Production VServer***")
                sh_vsvr(Message, 'ProdServer')
                send(Message, "************************")
                
            elif (msg == "sh bvsvr"):
                send(Message, "***Beta Test VServer***")
                sh_vsvr(Message, 'BetaServer')
                send(Message, "************************")
                
            else:
                unknown_cmd(Message)
        else:
            ###########
            # unknown #
            ###########
            logging.info("%s is unknown" % Message.FromHandle)
            send(Message, "***I see you.***")
            send(Message, "But...")
            send(Message, "***ha ha Bye~~***")
            


def send(Message, String):
    Message.Chat.SendMessage(String)



skype = Skype4Py.Skype();

# Read in user list from config.ini
admin_list = user_permission('admin')
op_list = user_permission('op')

logging.info("admin list: %s" % admin_list)
logging.info("op list: %s" % op_list)

# check input opts 
global prod_key
global beta_key
global prod_value
global beta_value

prod_key, beta_key, prod_value, beta_value = get_list()

skype.OnAttachmentStatus = on_attach
skype.OnMessageStatus = command 


if skype.Client.IsRunning == False: 
    skype.Client.Start() 

skype.Attach();

while True: 
    pass
    #time.sleep(0.3)
