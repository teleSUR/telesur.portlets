# -*- coding: utf-8 -*-

import random

from AccessControl import getSecurityManager

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.ATContentTypes.interfaces.topic import IATTopic
from collective.nitf.content import INITF

from collective.prettydate.interfaces import IPrettyDate

from telesur.portlets import _


class ILatestNITFPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Specify the maximum number of items to show in the "
                      u"portlet. Leave this blank to show all items."),
        default=10,
        required=False)


    pretty_date = schema.Bool(
        title=_(u'Pretty dates'),
        description=_(u"Show dates in a pretty format (ie. '4 hours ago')."),
        default=True,
        required=False)


    anonymous_only = schema.Bool(
        title=_(u'Anonymous only'),
        description=_(u"Display this portlet only for anonymous users."),
        default=True,
        required=False)


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ILatestNITFPortlet)

    limit = 10
    pretty_date = True
    anonymous_only = True

    def __init__(self,
                 limit = 10,
                 pretty_date=True,
                 anonymous_only=True):

        self.limit = limit
        self.pretty_date = pretty_date
        self.anonymous_only = anonymous_only

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return _(u"Latest NITF")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('latest_nitf.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        if self.data.anonymous_only and not portal_state.anonymous():
            return False

        return len(self.results()) > 0

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    @memoize
    def results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            limit = self.data.limit
            if limit and limit > 0:
                # pass on batching hints to the catalog
                results = collection.queryCatalog(batch=True, b_size=limit)
                results = results._sequence
            else:
                results = collection.queryCatalog()
            if limit and limit > 0:
                results = results[:limit]
        return results

    def collection(self):
        context = None
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        
        if (IPloneSiteRoot.providedBy(self.context) or
            IATTopic.providedBy(self.context)):
            self.kind = 'all'
            collection = 'todas-las-noticias'
            context = portal

        if INITF.providedBy(self.context):
            self.kind = 'section'
            normalizer = getUtility(IIDNormalizer)
            collection = normalizer.normalize(self.context.section)
            context = portal.get('noticias', None)

        if not context:
            return None

        result = context.get(collection, None)

        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None

        return result

    def getHeader(self):
        text = u"Noticias recientes"
        
        if self.kind == 'section':
            text += u" de %s" % self.context.section

        return text

    def getPrettyDate(self, date):
        # Returns human readable date for the tweet
        date_utility = getUtility(IPrettyDate)
        date = date_utility.date(date)

        return date

    def getMoreLink(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        
        if self.kind == 'all':
            context = portal
        else:
            context = self.collection()
            
        return context.absolute_url()
        
class AddForm(base.AddForm):

    form_fields = form.Fields(ILatestNITFPortlet)
    form_fields = form_fields.omit('target_collection')
    
    label = _(u"Add latest NITF Portlet")
    description = _(u"This portlet display a list of latest NITF from a "
                    u"Collection. It will select between different collections "
                    u"based on the current context.")


    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):

    form_fields = form.Fields(ILatestNITFPortlet)
    form_fields = form_fields.omit('target_collection')

    label = _(u"Add latest NITF Portlet")
    description = _(u"This portlet display a list of latest NITF from a "
                    u"Collection. It will select between different collections"
                    u"based on the current context.")
