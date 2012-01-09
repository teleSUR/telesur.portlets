# -*- coding: utf-8 -*-

import json
import logging
import urllib

from zope.component import getUtility
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from telesur.registry.interfaces import IDisqusSettings

from telesur.portlets.config import PROJECTNAME
from telesur.portlets import _


class IPopularThreads(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                             description=_(u"The header for the portlet. "
                                            "Leave empty for none."),
                             required=False)

    forum = schema.TextLine(title=_(u'Forum'),
                            description=_(u"Specify the forum you wish to "
                                           "obtain the popular threads from."),
                            required=True)

    max_results = schema.Int(title=_(u'Maximum results'),
                             description=_(u"The maximum results number."),
                             required=True,
                             default=5)

    interval = schema.TextLine(title=_(u'Interval'),
                               description=_(u"Choices: 1h, 6h, 12h, 1d, 7d, "
                                             "30d, 90d"),
                               required=True,
                               default=u"7d")


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPopularThreads)

    forum = u""
    max_results = 5
    header = None
    interval = u"7d"

    def __init__(self,
                 max_results,
                 interval,
                 forum,
                 header=None,):

        self.forum = forum
        self.max_results = max_results
        self.header = header
        self.interval = interval

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Popular Threads")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('popular_threads.pt')

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def getPopularPosts(self):
        base_url = ("https://disqus.com/api/3.0/threads/listPopular.json?"
                    "access_token=%s&api_key=%s&api_secret=%s&limit=%s"
                    "&interval=%s&forum=%s")

        result = []
        registry = getUtility(IRegistry)
        disqus = registry.forInterface(IDisqusSettings)
        url = base_url % (disqus.access_token,
                          disqus.app_public_key,
                          disqus.app_secret_key,
                          self.data.max_results,
                          self.data.interval,
                          self.data.forum)

        logger = logging.getLogger(PROJECTNAME)

        try:
            request = urllib.urlopen(url)
        except IOError, e:
            logger.error('urlopen error trying to access to the Disqus site - '\
                         'errno: "%i" - message: "%s".' \
                         % ( e.strerror.errno,  e.strerror.strerror))
        else:
            response = request.read()
            results = json.loads(response)

            if results['code'] != 0:
                logger.error('Disqus API error - '\
                             'code: %(code)i - response: %(response)s - '\
                             'See "http://disqus.com/api/docs/errors/" ' \
                             'for more details' % results)
            else:
                result = results['response']

        finally:
            return result


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IPopularThreads)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPopularThreads)
