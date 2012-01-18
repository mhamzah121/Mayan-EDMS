from __future__ import absolute_import

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist

from permissions.models import StoredPermission

from .managers import AccessEntryManager, DefaultAccessEntryManager
from .classes import AccessObjectClass
from .api import get_classes

logger = logging.getLogger(__name__)

        
class AccessEntry(models.Model):
    """
    Model that hold the permission, object, actor relationship
    """
    permission = models.ForeignKey(StoredPermission, verbose_name=_(u'permission'))

    holder_type = models.ForeignKey(
        ContentType,
        related_name='access_holder',
        limit_choices_to={'model__in': ('user', 'group', 'role')}
    )
    holder_id = models.PositiveIntegerField()
    holder_object = generic.GenericForeignKey(
        ct_field='holder_type',
        fk_field='holder_id'
    )

    content_type = models.ForeignKey(
        ContentType,
        related_name='object_content_type'
    )
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )

    objects = AccessEntryManager()

    class Meta:
        verbose_name = _(u'access entry')
        verbose_name_plural = _(u'access entries')

    def __unicode__(self):
        return u'%s: %s' % (self.content_type, self.content_object)


class DefaultAccessEntry(models.Model):
    """
    Model that holds the permission, class, actor relationship, that will
    be added upon the creation of an instance of said class
    """
    @classmethod
    def get_classes(cls):
        return [AccessObjectClass.encapsulate(cls) for cls in get_classes()]
    
    permission = models.ForeignKey(StoredPermission, verbose_name=_(u'permission'))

    holder_type = models.ForeignKey(
        ContentType,
        limit_choices_to={'model__in': ('user', 'group', 'role')},
        related_name='default_access_entry_holder'
    )
    holder_id = models.PositiveIntegerField()
    holder_object = generic.GenericForeignKey(
        ct_field='holder_type',
        fk_field='holder_id'
    )

    content_type = models.ForeignKey(
        ContentType,
        related_name='default_access_entry_class'
    )

    objects = DefaultAccessEntryManager()

    class Meta:
        verbose_name = _(u'default access entry')
        verbose_name_plural = _(u'default access entries')

    def __unicode__(self):
        return u'%s: %s' % (self.content_type, self.content_object)
