# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

#url conf
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

def required(wrapping_functions,patterns_rslt):
    '''
    Used to require 1..n decorators in any view returned by a url tree

    Usage:
      urlpatterns = required(func,patterns(...))
      urlpatterns = required((func,func,func),patterns(...))

    Note:
      Use functools.partial to pass keyword params to the required 
      decorators. If you need to pass args you will have to write a 
      wrapper function.

    Example:
      from functools import partial

      urlpatterns = required(
          partial(login_required,login_url='/accounts/login/'),
          patterns(...)
      )
    '''
    if not hasattr(wrapping_functions,'__iter__'): 
        wrapping_functions = (wrapping_functions,)

    return [
        _wrap_instance__resolve(wrapping_functions,instance)
        for instance in patterns_rslt
    ]

def _wrap_instance__resolve(wrapping_functions,instance):
    if not hasattr(instance,'resolve'): return instance
    resolve = getattr(instance,'resolve')

    def _wrap_func_in_returned_resolver_match(*args,**kwargs):
        rslt = resolve(*args,**kwargs)

        if not hasattr(rslt,'func'):return rslt
        f = getattr(rslt,'func')

        for _f in reversed(wrapping_functions):
            # @decorate the function from inner to outter
            f = _f(f)

        setattr(rslt,'func',f)

        return rslt

    setattr(instance,'resolve',_wrap_func_in_returned_resolver_match)

    return instance

#Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #mom_home
    url(r'^$','mom_home.views.index'),
    url(r'^information/$','mom_home.views.information'),
    url(r'^onskelista/$','mom_home.views.onskelista'),
    url(r'^integritetspolicy/$','mom_home.views.integritetspolicy'),
    
    #mom_invite
    url(r'^inbjudan/$','mom_invite.views.index'),
    url(r'^inbjudan/gast/ny/$','mom_invite.views.new_guest'),
    url(r'^inbjudan/gast/(?P<guest_id>\d+)/(?P<action>[\w\-]+)/$','mom_invite.views.guest'),
    
    #django-registration
    url(r'^inbjudan/', include('registration.urls')),

    # admin    
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^robots\.txt$', direct_to_template,
     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
                           
)

urlpatterns += required(
    login_required,
    patterns('',
     #blogg
     (r'^blogg/', include('zinnia.urls')),
     (r'^kommentarer/', include('django.contrib.comments.urls')),
    )
)