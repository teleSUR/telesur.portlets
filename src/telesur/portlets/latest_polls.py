# -*- coding: utf-8 -*-

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from time import time

from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
#from collective.prettydate.interfaces import IPrettyDate

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from telesur.portlets import _
            

class ILatestPolls(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                             description=_(u"The header for the portlet. "
                                            "Leave empty for none."),
                             required=False)

    max_results = schema.Int(title=_(u'Maximum results'),
                             description=_(u"The maximum results number."),
                             required=True,
                             default=5)

    #pretty_date = schema.Bool(title=_(u'Pretty dates'),
                              #description=_(u"Show dates in a pretty format (ie. '4 hours ago')."),
                              #default=True,
                              #required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ILatestPolls)

    max_results = 5
    header = None
    #pretty_date = True

    def __init__(self,
                 max_results,
                 header=None):
                 #pretty_date=True):

        self.max_results = max_results
        self.header = header
        #self.pretty_date = pretty_date

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Latest polls")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('latest_polls.pt')

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def getLatestPolls(self):
        """
        """
        pc = getToolByName(self.context, 'portal_catalog')

        return pc({'portal_type':'collective.polls.poll',
                   'sort_on':'created',
                   'sort_order':'reverse'})

    #def getDate(self, date):
        #if self.data.pretty_date:
            ## Returns human readable date
            #date_utility = getUtility(IPrettyDate)
            #date = date_utility.date(date)
            
        #return date


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ILatestPolls)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ILatestPolls)
