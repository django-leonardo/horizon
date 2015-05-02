
import os
from datetime import datetime

from django.db import models
from django.utils.timezone import get_current_timezone, make_aware, now
from django.utils.translation import ugettext_lazy as _
from filer import settings as filer_settings
from filer.models.abstract import BaseImage
from filer.models.filemodels import File
from filer.models.foldermodels import Folder


class MediaMixin(object):

    @classmethod
    def matches_file_type(cls, iname, ifile=None, request=None):
        # the extensions we'll recognise for this file type
        # (majklk): TODO move to settings or live config
        filename_extensions = getattr(cls, 'filename_extensions', '*')
        ext = os.path.splitext(iname)[1].lower()
        return ext in filename_extensions


class LeonardoFolder(Folder):

    class Meta:
        verbose_name = ("folder")
        verbose_name_plural = ('folders')
        app_label = 'media'


class Document(MediaMixin, File):

    filename_extensions = ['.pdf', '.xls', ]

    class Meta:
        verbose_name = ("document")
        verbose_name_plural = ('documents')


class Vector(MediaMixin, File):

    filename_extensions = ['.svg', '.eps', ]

    class Meta:
        verbose_name = ("vector")
        verbose_name_plural = ('vetors')


class Video(MediaMixin, File):

    filename_extensions = ['.dv', '.mov', '.mp4', '.avi', '.wmv', ]

    class Meta:
        verbose_name = ("video")
        verbose_name_plural = ('videos')


class Image(MediaMixin, BaseImage):

    filename_extensions = ['.jpg', '.jpeg', '.png', '.gif', ]

    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True,
                                      editable=False)

    author = models.CharField(
        _('author'), max_length=255, null=True, blank=True)

    must_always_publish_author_credit = models.BooleanField(
        _('must always publish author credit'), default=False)
    must_always_publish_copyright = models.BooleanField(
        _('must always publish copyright'), default=False)

    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.exif.get('DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = exif_date.split(" ")
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    if getattr(settings, "USE_TZ", False):
                        tz = get_current_timezone()
                        self.date_taken = make_aware(datetime(
                            int(year), int(month), int(day),
                            int(hour), int(minute), int(second)), tz)
                    else:
                        self.date_taken = datetime(
                            int(year), int(month), int(day),
                            int(hour), int(minute), int(second))
            except Exception:
                pass
        if self.date_taken is None:
            self.date_taken = now()
        super(Image, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _('images')

        # You must define a meta with en explicit app_label
        app_label = 'media'