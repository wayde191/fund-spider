#!/usr/bin/python
#-*-coding:utf-8-*-

import APNSWrapper
import binascii

class iHPush:
    def __init__(self):
        self.wrapper = APNSWrapper.APNSNotificationWrapper('/root/dis_ifno.pem', False)
        self.wrapperPro = APNSWrapper.APNSNotificationWrapper('/root/pro_ifno.pem', False)
#        self.wrapper = APNSWrapper.APNSNotificationWrapper('/Users/wayde/Workspace/iHakulaSVN/python/PythonLearn/dis_ifno.pem', False)
#        self.wrapperPro = APNSWrapper.APNSNotificationWrapper('/Users/wayde/Workspace/iHakula/python/PythonLearn/pro_ifno.pem', False)

    def push(self, token='', alertmessage='', ubadge=0, ttype=''):
        deviceToken = binascii.unhexlify(token)
        message = APNSWrapper.APNSNotification()
        message.token(deviceToken)
        message.badge(1)
        message.alert(alertmessage)
        message.sound()
        if "nonfree" == ttype:
            self.wrapperPro.append(message)
        else:
            self.wrapper.append(message)
    
    def notify(self):
        self.wrapper.notify()
        self.wrapperPro.notify()

#p = iHPush()
#p.push("b92367d8c6966edd138dca903811d6588a3fc4b8999c33a4692db5b25ee77e40", "haha", 0);
#p.push("e879c79e32fd25e776f21501656b0c7884287f9b8f9cefa345c93763e211cd81", "yayalele", 0);
#p.push("b92367d8c6966edd138dca903811d6588a3fc4b8999c33a4692db5b25ee77e40", "nono", 0);
#p.notify()
#feedback = APNSWrapper.APNSFeedbackWrapper('/Users/wayde/Workspace/iHakula/python/PythonLearn/pro_ifno.pem', False)
#feedback.receive()
#print "\n".join("%s at %s" % (binascii.hexlify(y), x.strftime("%m %d %Y %H:%M:%S")) for x, y in feedback)
