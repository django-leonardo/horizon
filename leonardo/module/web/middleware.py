# -*- coding: UTF-8 -*-
import datetime
import json
import logging
import os
import time
from datetime import datetime, timedelta

import six
from django import http, shortcuts
from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib import auth
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.models import Site
from django.core import exceptions, urlresolvers
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import loading
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.encoding import iri_to_uri
from django.utils.translation import ugettext as __
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from feincms.content.application.models import reverse
from .models import Page
from horizon import exceptions, messages


class WebMiddleware(object):

    """add extra context to request

    added some extra to request and page

    note: for support old ``webcms`` stuff adds some
    extra stuff which would be old after migration

    """

    def process_request(self, request):
        try:
            leonardo_options = {
                'meta_description': config_value('WEB', 'META_KEYWORDS'),
                'meta_keywords': config_value('WEB', 'META_DESCRIPTION'),
                'meta_title': config_value('WEB', 'META_TITLE'),
            }
            is_private = config_value('WEB', 'IS_PRIVATE')
        except:
            leonardo_options = {
                'meta_description': '',
                'meta_keywords': '',
                'meta_title': '',
            }
            is_private = False

        leonardo_options['site'] = {
            'name': settings.SITE_NAME,
            'id': settings.SITE_ID,
            'domain': getattr(
                settings, 'SITE_DOMAIN', settings.SITE_NAME + '.cz'),
        }

        try:
            page = Page.objects.best_match_for_path(
                request.path)

            # TODO: find better solution
            widgets = []
            for k, val in six.iteritems(page._ct_inventory):
                if k != '_version_':
                    widgets += getattr(page.content, k, [])
            leonardo_options['widgets'] = widgets
        except Exception:
            page = None
            leonardo_options['template'] = 'base.html'
            leonardo_options['theme'] = 'light'
            leonardo_options['assets'] = []
            leonardo_options['widgets'] = []

        leonardo_options['is_private'] = is_private
        request.leonardo_options = leonardo_options
        request.leonardo_page = page
        request.frontend_editing = request.COOKIES.get(
            'frontend_editing', False)
        # old
        request.webcms_page = page
        request.webcms_options = leonardo_options