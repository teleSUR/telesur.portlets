# -*- coding: utf-8 -*-
from time import time
from zope.component import getUtility


from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.memoize import ram
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
#from collective.prettydate.interfaces import IPrettyDate

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from openmultimedia.api.interfaces import IVideoAPI

from telesur.portlets import _


class IRecentVideos(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    tag = schema.TextLine(title=_(u'Tag'),
                          description=_(u"Tag to filter the videos "),
                          required=True)

    limit = schema.Int(title=_(u'Limit'),
                       description=_(u"The maximum results number."),
                       required=True,
                       default=5)


def cache_key_simple(func, var):
    #let's memoize for 5 minutes or if any value of the tile is modified.
    timeout = time() // (60 * 5)
    return (timeout,)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRecentVideos)

    max_results = 5
    header = None
    #pretty_date = True

    def __init__(self,
                 tag,
                 limit):

        self.limit = limit
        self.tag = tag

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Recent videos")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('recent_videos.pt')

    def getTag(self):
        """
        Returns the tag for the portlet
        """
        return self.data.tag

    def getLimit(self):
        """
        Returns the limit for the portlet
        """
        return self.data.limit

    #@ram.cache(cache_key_simple)
    def results_video(self):
        video_api = getUtility(IVideoAPI)
        url = video_api.get_section_tag_clip_list(
            tag=self.getTag(), offset=0, limit=self.getLimit()
        )
        content_json = video_api.get_json(url)
        return content_json


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRecentVideos)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRecentVideos)
