# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime, date, timedelta
from django.utils.timezone import utc
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger('MOM_HOME');

def index(request):    
    logger.info("Show index")
    try:
        time_left = datetime.strptime('Jun 8 2013  5:00PM', '%b %d %Y %I:%M%p') - datetime.now()
    except:
        time_left = None
    return render_to_response('mom_home/index.html', {'title':'Välkommen!', 
                                                      'page_name':'index',
                                                      'time_left':time_left,},  RequestContext(request))

@login_required
def information(request):
    logger.info("Show information")
    return render_to_response('mom_home/information.html', {'title': 'Information', 'page_name':'information'},  RequestContext(request))

@login_required
def onskelista(request):
    logger.info("Show information")
    return render_to_response('mom_home/onskelista.html', {'title': 'Önskelista', 'page_name':'information'},  RequestContext(request))

@login_required
def integritetspolicy(request):
    logger.info("Show integritetspolicy")
    return render_to_response('mom_home/integritetspolicy.html', {'title': 'Integritetspolicy', 'page_name':'index'},  RequestContext(request))