'''
Created on Oct 6, 2020

@author: dsm
'''
#import os
#from django.shortcuts import render
#from django.conf import settings
from django.http import HttpResponse, JsonResponse
import requests, time, json

ENDTRACERESPONSE='trace1-OK'
TESTPREFIX='[{"trace1end"'

def health(request):
    return HttpResponse("OK")


def trace1(request):
    next = request.GET.get('next', '')
    hop = int(request.GET.get('hop', 0)) + 1
    nexthost, nextlist, hopsleft = splitnext(next)
    
    geturl="http://"+nexthost+"/trace1?next="+nextlist+"&hop="+str(hop)
    scode=0
    reason=""
    text="**"
    etime = None
    stime = time.time()
    err=0
    cip=get_client_ip(request)
    sip=request.get_host()
   
    if next=='':
        tt=[{"trace1end":ENDTRACERESPONSE, "hopsleft":hopsleft-1, "sip":sip, "cip":cip}]
        return (JsonResponse(tt, safe=False))
   
    
    try:
        rr = requests.request(url=geturl,timeout=1 + hopsleft, method="GET")
        
        etime = exec_time(stime)
        scode=rr.status_code
        reason=rr.reason
        text=rr.text
        
    
    except Exception as ex:
        if etime == None:
            etime = exec_time(stime)
        err=1
    
    
    if text.find(TESTPREFIX, 0, len(TESTPREFIX)) == -1:
        text='[{"trace1end": "OTHER","hopsleft":'+str(hopsleft-1)+'}]' 
    
    jresp=json.loads(text)
    tt={"hop":hop, "host":nexthost, "scode":scode, "reason":reason, "err":err , "etime":etime, "sip":sip, "cip":cip}
    jresp.append(tt)
    #jresp.append(tt)
    

    return JsonResponse(jresp, safe=False)
    

def splitnext(n):
    #pop off the next host, operating on a string instead of an array like pop()
    a=n.split(",")
    alength = len(a)
    if alength > 1:
        nn = ",".join(a[1:])
        return (a[0], nn, alength)
    return (a[0], '', alength)
    
def exec_time(st):
    return int((time.time() -st) * 1000)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip