# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope.component import getUtility
from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.prettydate.interfaces import IPrettyDate

from telesur.portlets import _


class IFilterKeywordNITFPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    keyword = schema.TextLine(
        title=_(u"keyword"),
        description=_(u"Filter Nitf by keyword"),
        required=True)

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


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFilterKeywordNITFPortlet)

    limit = 10
    pretty_date = True

    def __init__(self,
                 keyword,
                 limit=10,
                 pretty_date=True):

        self.keyword = keyword
        self.limit = limit
        self.pretty_date = pretty_date

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return _(u"Latest NITF")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('nitf_tag.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return len(self.results())

    def get_limit(self):
        limit = 10
        if self.data.limit:
            limit = self.data.limit
        return limit

    def get_keyword(self):
        return self.data.keyword

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    #@memoize
    def results(self):
        results = []
        query = {'portal_type': 'collective.nitf.content',
                 'sort_on': 'effective', 'sort_order': 'descending',
                 'review_state': 'published'}
        keyword = self.get_keyword()
        if keyword:
            query['Subject'] = tuple([item.strip() for item in keyword.split(",")])
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)
        return results[:self.get_limit()]

    def getHeader(self):
        text = u"Noticias recientes"
        return text

    def getPrettyDate(self, date):
        # Returns human readable date for the tweet
        date_utility = getUtility(IPrettyDate)
        date = date_utility.date(date)

        return date


class AddForm(base.AddForm):

    form_fields = form.Fields(IFilterKeywordNITFPortlet)

    label = _(u"Add latest NITF Portlet Filtered by Keyword")
    description = _(u"This portlet display a list of latest NITF filtered "
                    u"by a Keyword")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    form_fields = form.Fields(IFilterKeywordNITFPortlet)

    label = _(u"Add latest NITF Portlet Filtered by Keyword")
    description = _(u"This portlet display a list of latest NITF filtered by Keyword")
