# -*- coding: utf-8 -*-
from django import template
from mom_invite.models import Guest

register = template.Library()

def show_guest(the_guest):
    return {'the_guest':the_guest,}
        
register.inclusion_tag('mom_invite/guest.html')(show_guest)