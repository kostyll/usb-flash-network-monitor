# -*- coding : utf-8 -*-
# from __future__ import unicode_literals

import os
import re
import urllib2, urllib


def get_env_login_pass():
    try:
        login = os.environ['EPOCHTA_LOGIN']
    except KeyError:
        raise Exception('NOT SET EPOCHTA_LOGIN')
    try:
        password = os.environ['EPOCHTA_PASS']
    except KeyError:
        raise Exception('NOT SET EPOCHTA_PASS')
    return login,password

class cleared_response_from_request(object):
    def __init__(self,re_expr):
        self.re_expr = re_expr if isinstance(re_expr, (tuple,list)) else (re_expr,)

    def __call__(self,func):
        def wrapper(*args,**kwargs):
            result = func(*args,**kwargs)
            results = [re.compile(pattern).findall(result) for pattern in self.re_expr]
            for index,result in enumerate(results):
                if isinstance(result,(tuple,list)):
                    if len(result) == 1:
                        results[index] = result[0]
            return results
        return wrapper


def request_template_as_request(func):
    def wrapper(*args,**kwargs):
        result = func(*args,**kwargs)
        senddata=[('XML',result)]
        senddata=urllib.urlencode(senddata)
        path='http://atompark.com/members/sms/xml.php'
        req=urllib2.Request(path, senddata)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        result=urllib2.urlopen(req).read()
        return result
    return wrapper

status_pattern = r'<status>([a-zA-Z0-9]+)</status'
credits_pattern = r'<credits>([0-9\.]+)</credits>'

@cleared_response_from_request((
        status_pattern,
        credits_pattern))
@request_template_as_request
def send_sms(login,password,sender,text,msg_id,phone_sms):
    return '''<?xml version="1.0" encoding="UTF-8"?>
                <SMS>
                <operations>
                <operation>SEND</operation>
                </operations>
                <authentification>
                <username>{}</username>
                <password>{}</password>
                </authentification>
                <message>
                <sender>{}</sender>
                <text>{}</text>
                </message>
                <numbers>
                <number messageID="{}">{}</number>
                </numbers>
                </SMS>'''.format(login, password, sender, text, msg_id, phone_sms)

@cleared_response_from_request(r'<message id="([a-zA-Z0-9]+)" sentdate="[0-9\:\-\ ]+" donedate="[0-9:\-\ ]+" status="([0-9]+)" />')
@request_template_as_request
def get_sms_status(login,password,msg_id):
    return '''<?xml version="1.0" encoding="UTF-8"?>
            <SMS>
            <operations>
            <operation>GETSTATUS</operation>
            </operations>
            <authentification>
            <username>{}</username>
            <password>{}</password>
            </authentification>
            <statistics>
            <messageid>{}</messageid>
            </statistics>
            </SMS>'''.format(login, password, msg_id)

@cleared_response_from_request((
        r'<status>([a-zA-Z0-9]+)</status',
        r'<credits>([0-9\.]+)</credits>' ))
@request_template_as_request
def get_send_price (login,password,sender,text,msg_id,phone_sms):
    return'''<?xml version="1.0" encoding="UTF-8"?>
            <SMS>
            <operations>
            <operation>GETPRICE</operation>
            </operations>
            <authentification>
            <username>{}</username>
            <password>{}</password>
            </authentification>
            <message>
            <sender>{}</sender>
            <text>{}</text>
            </message>
            <numbers>
            <number messageID="{}">{}</number>
            </numbers>
            </SMS>'''.format(login, password, sender, text, msg_id, phone_sms)

@cleared_response_from_request((
        r'<status>([a-zA-Z0-9]+)</status',
        r'<credits>([0-9\.]+)</credits>'))
@request_template_as_request
def get_balance(login,password):
    return '''<?xml version="1.0" encoding="UTF-8"?>
            <SMS>
            <operations>
            <operation>BALANCE</operation>
            </operations>
            <authentification>
            <username>{}</username>
            <password>{}</password>
            </authentification>
            </SMS>'''.format(login, password)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        action='store',
                        choices=('send-sms','get-balance','get-sms-status','get-sms-price','help'),
                        help='type action',
                        )
    parser.add_argument('-u',
                        '--user',
                        dest='user',
                        action='store',
                        type=str,
                        help='user login',
                        default=None,
                        )
    parser.add_argument('-p',
                        '--pass',
                        dest='password',
                        action='store',
                        type=str,
                        help='user password',
                        default=None,
                        )
    parser.add_argument('-s',
                        '--sender',
                        dest='sender',
                        action='store',
                        type=str,
                        help='sender name',
                        default='sms',
                        )
    parser.add_argument('-m',
                        '--message',
                        dest='message',
                        action='store',
                        type=str,
                        help='message text',
                        default=None,
                        )
    parser.add_argument('-d',
                        '--destination-number',
                        dest='destination_number',
                        action='store',
                        type=str,
                        help='destination recipient number',
                        default=None,
                        )
    parser.add_argument('-i',
                        '--message-id',
                        dest='message_id',
                        action='store',
                        type=str,
                        help='id for identification message',
                        default='FastMessage',
                        )

    def error_msg(msg):
        print (msg)
        parser.print_help()
        os.sys.exit(0)

    args = parser.parse_args()

    if args.action == "help":
        parser.print_help()
        os.sys.exit(0)

    action = args.action
    login,password = args.user,args.password
    text = args.message
    msg_id = args.message_id
    sender = args.sender
    phone_sms = args.destination_number

    if (login is None) or (password is None):
        try:
            login = os.environ['EPOCHTA_LOGIN']
            password = os.environ['EPOCHTA_PASS']
        except KeyError:
            error_msg("You must specify login,pass in cli \nor in the environment puttin EPOCHTA_LOGIN,EPOCHTA_PASS into it\n")
    if action == 'send-sms':
        if text is None:
            error_msg("you must specify message text")
        if phone_sms is  None:
            error_msg("you must specify destination number")
        status, credits = send_sms(login,password,sender,text,msg_id,phone_sms)
        if int(status) <= 0:
            error_msg("message id={} isn't put in delivery queue...".format(msg_id))
        else:
            print("message id={} is put in delivery queue...".format(msg_id))

    elif action == 'get-balance':
        status,credits = get_balance(login,password)
        if int(status) != 0:
            error_msg("Can't retrive balance...")
        else:
            print ("your balance is {}".format(credits))

    elif action == 'get-sms-price':
        if text is None:
            error_msg("you must specify message text")
        if phone_sms is  None:
            error_msg("you must specify destination number")
        status, credits = get_send_price(login,password,sender,text,msg_id,phone_sms)
        if int(status) != 0:
            error_msg("Can't retrive price...")
        else:
            print("Cost of sending is {}".format(credits))

    elif action == 'get-sms-status':
        if msg_id is None:
            error_msg("you must specify message id...")
        statuses = get_sms_status(login,password,msg_id)

        for status in statuses[0]:
            print ("message_id[{}] is {}".format(*status))

if __name__ == "__main__":
    main()
