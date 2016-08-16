#!/usr/bin/python
#-*-coding:utf-8-*-

import httplib, urllib, re
from datetime import *
from push import *
import time
import MySQLdb

class iHDate:
    def __init__(self):
        self.date = date.today()

    def isTodayMonday(self):
        if self.date.weekday() == 0:
            return True
        else:
            return False

    def isTodayFriday(self):
        if self.date.weekday() == 4:
            return True
        else:
            return False

    def isTodaySaturday(self):
        if self.date.weekday() == 5:
            return True
        else:
            return False

    def isTodayWeekend(self):
        if (self.date.weekday() == 6):
            return True
        else:
            return False

    def getThedayString(self, distance = 0):
        yestarday = date.today() + timedelta(distance)
        return yestarday.isoformat()
    
    def getDateString(self):
        return self.date.isoformat()

    def getYestardayString(self):
        yestarday = date.today() + timedelta(-1)
        return yestarday.isoformat()

    def getDayBeforeYestardayString(self):
        daybeforeYestarday = date.today() + timedelta(-2)
        return daybeforeYestarday.isoformat()

    def getCurrentDateTimeStr(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class iHRequest:
    def __init__(self, keyValues=[]):
        self.keyValues = keyValues
    
    def dispatch(self):
        return {
            'fund': self.fund(),
        }[self.keyValues[0]]

    def fund(self):
        conn = httplib.HTTPConnection(self.keyValues[2])
        conn.request("GET", self.keyValues[3])
        response = conn.getresponse()
        htmlData = response.read()

        collectionData = [];
        regs = self.keyValues[4].split(',', 1)
        for reg in regs:
            reg = reg.strip()
            htmlValue = re.findall(reg, htmlData)
            collectionData.append(htmlValue)

        conn.close()
        return collectionData

class iHMysql:
    def __init__(self, fundBasic=[], fundValues=[]):
        self.fundBasic = fundBasic
        self.fundValues = fundValues

    def getConnection(self):
#        return  MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='ihakula',port=3306, charset="utf8")
        return  MySQLdb.connect(host='127.0.0.1',user='root',passwd='Wayde191!',db='ihakula',port=3306, charset="utf8")

    def insertOne(self):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "insert into ih_funds(name,million_revenue,sevenday_revenue,date) values(%s,%s,%s,%s)"
            today = iHDate()
            param = (self.fundBasic[1], self.fundValues[0][0], self.fundValues[1][0], today.getYestardayString())
            n = cur.execute(sql,param)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def insertTwo(self):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "insert into ih_funds(name,million_revenue,sevenday_revenue,date) values(%s,%s,%s,%s)"
            today = iHDate()

            param = (self.fundBasic[1], self.fundValues[0][0], self.fundValues[1][0], today.getYestardayString())
            n = cur.execute(sql,param)
            conn.commit()
            
            param = (self.fundBasic[1], self.fundValues[0][1], self.fundValues[1][1], today.getDayBeforeYestardayString())
            n = cur.execute(sql,param)
            conn.commit()
            
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def getFundIdByName(self, fname):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "select ID from ih_fund where name=%s"
            n = cur.execute(sql, [fname.split('(')[0]])
            fid = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            return fid
        
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def getRateById(self, frates = [], fid = 0):
        try:
            for r in frates:
                if fid == r[0]:
                    return r[1]
            return 0
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    def updateConfirms(self, dayCount = 1):
        try:
            today = iHDate()
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "select * from ih_if_certification_cash where approve_date=%s and verified=0 order by apply_date asc"
            param = [today.getDateString()]
            if 2 == dayCount:
                param = [today.getYestardayString()]
            n = cur.execute(sql, param)
            rows = cur.fetchall()
            
            for row in rows:
                accountId = row[1]
                sql = "select * from ih_if_account where ID=%s"
                param = [accountId]
                n = cur.execute(sql, param)
                account = cur.fetchone()
                
                cashArr = row[2].split(',')
                verifiedCashArr = account[3].split(',')
                
                for fcash in cashArr:
                    founded = False
                    fkeyvalue = fcash.split(':')
                    fid = fkeyvalue[0]
                    fvalue = fkeyvalue[1]
                    for vcash in verifiedCashArr:
                        objectIndex = verifiedCashArr.index(vcash)
                        vkeyvalue = vcash.split(':')
                        vid = vkeyvalue[0]
                        vvalue = vkeyvalue[1]
                        if fid == vid:
                            verifiedValue = float(fvalue) + float(vvalue)
                            verifiedValue = float("%.4f" % verifiedValue)
                            verifiedCash = str(vid) + ':' + str(verifiedValue)
                            verifiedCashArr[objectIndex] = verifiedCash
                            founded = True
                            break
            
                    if False == founded:
                        verifiedCashArr.append(fcash)
            
                sep = ','
                verifiedCashStr = sep.join(verifiedCashArr)
                sql = "update ih_if_account set purchased=%s, date=%s where ID=%s"
                param = [verifiedCashStr, today.getCurrentDateTimeStr(), accountId]
                n = cur.execute(sql, param)
                conn.commit()
                sql = "update ih_if_certification_cash set verified=%s where ID=%s"
                param = [1, row[0]]
                n = cur.execute(sql, param)
                conn.commit()

            cur.close()
            conn.close()
        
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def getAllFunds(self):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "select * from ih_fund order by ID asc"
            n = cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            fundsIDArr = []
            for row in rows:
                fundsIDArr.append(row[0]);
    
            return fundsIDArr
    
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def getFundsDayRevenue(self, date = ''):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            
            fundsRevenueDic = {}
            allfundsIDArr = self.getAllFunds()
            
            for fid in allfundsIDArr:
                sql = "SELECT million_revenue FROM ih_funds where name = (select concat(name,'(',code,')') as fundname from ih_fund where ID = %s) and date = %s"
                param = [fid, date]
                n = cur.execute(sql, param)
                row = cur.fetchone()
                if row:
                    fundsRevenueDic[fid] = row[0]
                
            cur.close()
            conn.close()
            
            return fundsRevenueDic
        
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def pushNotification(self, dayCount = 1):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            sql = "select * from ih_if_account order by ID asc"
            n = cur.execute(sql)
            rows = cur.fetchall()
            
            today = iHDate()
            settlementDate = today.getYestardayString()
            if 2 == dayCount:
                settlementDate = today.getDayBeforeYestardayString()
            fundsRevenueDic = self.getFundsDayRevenue(settlementDate)
            tokenMessageDic = {}
            tokenFreeDic = {}
            for row in rows:
                accID = row[0]
                token = row[2]
                purchased = row[3]
                allMoney = row[4]
                
                if token == '':
                    continue
                
                tokenFreeDic[token] = row[6]
                
                verifiedCashArr = purchased.split(',')
                allearn = 0
                for vcash in verifiedCashArr:
                    vkeyvalue = vcash.split(':')
                    fid = vkeyvalue[0]
                    rate = fundsRevenueDic.get(long(fid))
                    if rate != None:
                        income = float(rate) * float(vkeyvalue[1]) / 10000
                        allearn += income
                        if income > 0:
                            # Insert new income
                            sql = "insert into ih_if_income(account_id,fund_id,income,date) values(%s,%s,%s,%s)"
                            param = (accID, fid, income, today.getDateString())
                            cur.execute(sql,param)
                            conn.commit()
                            
                            # Insert new buy
                            dayAfter = 2
                            if today.isTodayFriday():
                                dayAfter = 4;
                            elif today.isTodaySaturday():
                                dayAfter = 3;
                            sql = "insert into ih_if_certification_cash(account_id,cash,verified,approve_date,apply_date) values(%s,%s,%s,%s,%s)"
                            param = (accID, str(fid)+":"+str(income), 0, today.getThedayString(dayAfter), today.getDateString())
                            cur.execute(sql,param)
                            conn.commit()
                            
                            fundsMoneyArr = allMoney.split(',')
                            for oldcash in fundsMoneyArr:
                                oldIndex = fundsMoneyArr.index(oldcash)
                                oldkeyvalue = oldcash.split(':')
                                oldfid = oldkeyvalue[0]
                                if str(oldfid) == str(fid):
                                    newDisValue = float(oldkeyvalue[1]) + income
                                    newDisValue = float('%.4f' % newDisValue)
                                    fundsMoneyArr[oldIndex] = str(oldfid) + ":" + str(newDisValue)
                                    sep = ','
                                    allMoney = sep.join(fundsMoneyArr)
                                    break
                                    
#                            re.findall("(?<!\d)2"+":[+-]?\d*(?:\.\d+)?",allMoney)
#                            oldDisValue = re.findall(str(fid) + ":([-+]?\d*\.?\d+)", allMoney)
#                            newDisValue = float(oldDisValue[0]) + income
#                            allMoney = re.sub(str(fid) + ":([-+]?\d*\.?\d+)", str(fid) + ":" + str(newDisValue), allMoney)

                tokenMessageDic[token] = float('%.2f'% allearn)
                if allearn > 0:
                    sql = "update ih_if_account set all_money=%s where ID=%s"
                    param = [allMoney, accID]
                    n = cur.execute(sql, param)
                    conn.commit()
            
            cur.close()
            conn.close()
            
            pushObj = iHPush()
            messageCount = 0
            for token in tokenMessageDic:
                messageCount = messageCount + 1
                revenue = tokenMessageDic[token]
                ttype = tokenFreeDic[token]
                if 0 == revenue:
                    continue
                if 100 > messageCount:
                    alertmsg = '您于'+settlementDate+'号的总收益为: '+ str(tokenMessageDic[token])+' RMB'
                    pushObj.push(token, alertmsg, 0, ttype)
                else:
                    pushObj.notify()
                    messageCount = 0
                    pushObj = iHPush()
        
            pushObj.notify()

        

        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def run():
    today = iHDate()
    if today.isTodayMonday():
        try:
            data = open('CollectionItems.txt')
            for each_line in data:
                line = each_line.split(':', 4)
                element = iHRequest(line)
                filterArr = element.dispatch()
                sql = iHMysql(line, filterArr)
                sql.insertTwo()
    
            updateSql = iHMysql()
            updateSql.updateConfirms(1)
            updateSql.pushNotification(1)
            updateSql.pushNotification(2)
    
        except IOError:
            print("The datafile is missing");
        return
    else:
        if today.isTodayWeekend():
            return
        else:
            try:
                data = open('CollectionItems.txt')
                for each_line in data:
                    line = each_line.split(':', 4)
                    element = iHRequest(line)
                    filterArr = element.dispatch()
                    sql = iHMysql(line, filterArr)
                    sql.insertOne()

                updateSql = iHMysql()
                # Saturday has nothing to confirm, do nothing
                updateSql.updateConfirms(1)
                updateSql.pushNotification(1)

            except IOError:
                print("The datafile is missing")

run()

# fund:天弘(000198):fund.eastmoney.com:/000198.html:<span class="ui-font-large ui-color-red ui-num">([\s\S]*?)</span>,<span class="ui-font-middle ui-color-red ui-num">([\s\S]*?)</span></dd></dl>
