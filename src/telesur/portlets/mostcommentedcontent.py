from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from telesur.portlets import _

import json
import urllib


class IMostCommentedContent(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)

    header = schema.TextLine(title=_(u'Header'),
                                    description=_(u"The header for the portlet. Leave empty for none."),
                                    required=False)
                                   
    app_public_key = schema.TextLine(title=_(u'Consumer Key'),
                              description=_(u"Public key for your application. "
                                             "You need to create an app here: "
                                             "http://disqus.com/api/"
                                             "applications"),
                              required=True)

    app_secret_key = schema.TextLine(title=_(u'Consumer Secret'),
                              description=_(u"Secret key for your "
                                             "application."),
                              required=True)

    access_token = schema.TextLine(title=_(u'Access token'),
                              description=_(u"Access token to make requests"),
                              required=True)

    forum = schema.TextLine(title=_(u'Forum'),
                            description=_(u"Specify the forum you wish to "
                                           "obtain the most commented "
                                           "content from."),
                              required=True)

    max_results =  schema.Int(title=_(u'Maximum results'),
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

    implements(IMostCommentedContent)

    app_public_key = u""
    app_secret_key = u""
    access_token = u""
    forum = u""
    max_results = 5
    header=None
    interval = u"7d"

    def __init__(self,
                 app_public_key,
                 app_secret_key,
                 access_token,
                 max_results,
                 interval,
                 forum,
                 header=None,):
                     
        self.app_public_key = app_public_key
        self.app_secret_key = app_secret_key
        self.access_token = access_token
        self.forum = forum
        self.max_results = max_results
        self.header = header
        self.interval = interval
        

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Most Commented Content")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('mostcommentedcontent.pt')

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header
        
    def getPopularPosts(self):
        url = ("https://disqus.com/api/3.0/threads/listPopular.json?"
               "access_token=%s&api_key=%s&api_secret=%s&limit=%s&interval=%s"
               "&forum=%s")

        results = json.load(urllib.urlopen(url  % (self.data.access_token,
                                                   self.data.app_public_key,
                                                   self.data.app_secret_key,
                                                   self.data.max_results,
                                                   self.data.interval,
                                                   self.data.forum)))

        return results['response']

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMostCommentedContent)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMostCommentedContent)