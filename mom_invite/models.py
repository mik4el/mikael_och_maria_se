# -*- coding: utf-8 -*-
from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in

from datetime import datetime, date, timedelta
from django.utils.timezone import utc

class UserProfile(models.Model):
    
    MOM_ATTEND_CHOICE_YES = 1
    MOM_ATTEND_CHOICE_NO = 2
    MOM_ATTEND_CHOICE_UNANSWERED = 3
    
    MOM_ATTEND_CHOICES = (
    (MOM_ATTEND_CHOICE_YES, 'Ja gärna'),
    (MOM_ATTEND_CHOICE_NO, 'Nej tyvärr'),
    (MOM_ATTEND_CHOICE_UNANSWERED, 'Inget svar'),
    )
    
    user = models.OneToOneField(User)
    name = models.CharField('Namn', max_length=255,blank=True, null=True)
    adress_line_1 = models.CharField('Adress (rad 1)', max_length=255,blank=True, null=True)
    adress_line_2 = models.CharField('Adress (rad 2)', max_length=255,blank=True, null=True)
    postnr = models.CharField('Postnummer', max_length=255, blank=True, null=True)
    postort = models.CharField('Postort', max_length=255, blank=True, null=True)
    country = models.CharField('Land', max_length=255, blank=True, null=True, default="Sverige")
    message = models.CharField('Meddelande', max_length=255,blank=True, null=True)
    did_add_guests = models.BooleanField('Har lagt till gäster', default=False)
    attend_choice = models.IntegerField('Deltar', choices=MOM_ATTEND_CHOICES, default=MOM_ATTEND_CHOICE_UNANSWERED)
    is_active = models.BooleanField('Aktiv', default=True)
    numberOfLogins = models.IntegerField('Antal inloggningar', blank=False, null=False, default=0)
    lastLogin = models.DateTimeField('Senaste inloggningen', blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    def is_attending(self):
        if self.attend_choice == UserProfile.MOM_ATTEND_CHOICE_YES:
            return True
        else:
            return False
        
    def has_answered(self):
        if self.attend_choice == UserProfile.MOM_ATTEND_CHOICE_UNANSWERED:
            return False
        else:
            return True
        
    def guests_invited(self):
        try:
            return Guest.objects.active_guests_for_user(self.user)
        except Guest.DoesNotExist:
            return None
   
OK_TO_SEND_CHOICES = ((True, 'Skicka'), (False, 'Skicka inte'))
ALCOHOL_OK_CHOICES = ((True, 'Dricker alkohol'), (False, 'Dricker inte alkohol'))
   
class GuestManager(models.Manager):
    def active_guests_for_user(self, the_user):
        try:
            active_guests = super(GuestManager, self).get_query_set().filter(user=the_user, is_active=True)
        except Guest.DoesNotExist:
            active_guests = None
        return active_guests

class Guest(models.Model):
   objects = GuestManager()

   MOM_GENDER_TYPE_MALE = 1
   MOM_GENDER_TYPE_FEMALE = 2
   MOM_GENDER_TYPE_NA = 3

   MOM_GENDER_TYPES = (
       (MOM_GENDER_TYPE_MALE, 'Man'),
       (MOM_GENDER_TYPE_FEMALE, 'Kvinna'),
       (MOM_GENDER_TYPE_NA, 'Vill ej uppge'),
   )
   
   user = models.ForeignKey(User)
   first_name = models.CharField('Förnamn', max_length=255)
   last_name = models.CharField('Efternamn', max_length=255)
   gender = models.IntegerField('Kön', choices=MOM_GENDER_TYPES, default=MOM_GENDER_TYPE_NA)
   mobile_number = models.CharField('Mobiltelefon', max_length=255, blank=True, null=True)
   email_address = models.EmailField('Epost-adress', blank=True, null=True)
   best_book = models.CharField('Vilken är din favoritbok?', max_length=255)
   food_comment = models.CharField('Allergier, övriga matpreferenser', max_length=255, blank=True, null=True)
   alcohol_ok = models.BooleanField('Vill du dricka alkohol?', default=True, choices=ALCOHOL_OK_CHOICES)
   receive_emails_ok = models.BooleanField('Vill du ha info och nyheter?', default=True, choices=OK_TO_SEND_CHOICES)
   is_active = models.BooleanField('Aktiv', default=True)
   added_at = models.DateTimeField('Skapad', auto_now_add = True)

   def __unicode__(self):
       return u'%s: %s' % (self.user, self.first_name)

#Signals for profile
def update_user_login(sender, user, **kwargs):
   now = datetime.utcnow().replace(tzinfo=utc)
   profile = user.get_profile()
   profile.lastLogin = now
   profile.numberOfLogins += 1
   profile.save()
   
user_logged_in.connect(update_user_login)

def new_user_created(sender, instance, created, **kwargs):
   if created:
       UserProfile.objects.create(user=instance)
       
#post_save.connect(new_user_created, sender=User)