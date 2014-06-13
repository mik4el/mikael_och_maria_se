# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils.safestring import SafeString
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User

from datetime import datetime, date, timedelta
from django.utils.timezone import utc
        
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.core.mail import mail_admins

from mom_invite.models import Guest, UserProfile
from mom_invite.forms import GuestForm

import logging
logger = logging.getLogger('MOM_INVITE');

@login_required
def index(request):
    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.id)
        profile = user.get_profile()
        guests = Guest.objects.active_guests_for_user(user)
        if request.method == "POST":
            if 'no_thanks_form' in request.POST:
                if request.POST["attend_status"]=="True":
                    profile.attend_choice = UserProfile.MOM_ATTEND_CHOICE_YES
                else:
                    profile.attend_choice = UserProfile.MOM_ATTEND_CHOICE_NO
                profile.save()
    return render_to_response('mom_invite/mom_invite_index.html', {'title': 'Din inbjudan', 
                                                                   'page_name':'mom_invite_index', 
                                                                   'profile':profile, 
                                                                   'guests':guests,},  RequestContext(request))

@login_required
def guest(request, guest_id, action):
    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.id)
        profile = user.get_profile()
        the_guest = get_object_or_404(Guest, pk=guest_id)
        if the_guest.user != user:
            raise PermissionDenied
        if action == "andra":
            action = "ändra guest"
            the_guestform = GuestForm(instance=the_guest)
            if request.method == "POST":
                the_guestform = GuestForm(request.POST, instance=the_guest)
                if the_guestform.is_valid():
                    the_guest = the_guestform.save(commit = False)
                    the_guest.save()
                    return HttpResponseRedirect('/inbjudan/')            
        elif action == "tabort":
            action = "tabort guest"
            the_guest.delete()
            return HttpResponseRedirect('/inbjudan/')            
    return render_to_response('mom_invite/mom_invite_guest.html', {'title': 'Ändra gäst', 
                                                                   'page_name':'mom_invite_index', 
                                                                   'profile':profile, 
                                                                   'action':action, 
                                                                   'the_guest':the_guest,
                                                                   'the_guestform':the_guestform,
                                                                   'submit_name':'Spara',},  RequestContext(request))

@login_required
def new_guest(request):
    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.id)
        profile = user.get_profile()
        the_guestform = GuestForm()
        if request.method == "POST":
            the_guestform = GuestForm(request.POST)
            if the_guestform.is_valid():
                the_guest = the_guestform.save(commit = False)
                the_guest.user = user
                the_guest.save()
                return HttpResponseRedirect('/inbjudan/')
    return render_to_response('mom_invite/mom_invite_guest.html', {'title': 'Skapa ny gäst', 
                                                                   'page_name':'mom_invite_index', 
                                                                   'profile':profile,
                                                                   'the_guestform':the_guestform,
                                                                   'submit_name':'Lägg till',},  RequestContext(request))