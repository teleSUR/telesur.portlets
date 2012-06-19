from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.security import checkPermission

from telesur.portlets import _


class IUtilLinks(IPortletDataProvider):
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


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IUtilLinks)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Util links")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('utillinks.pt')

    def _checkPermInFolder(self, perm, folder_id):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        try:
            folder = portal[folder_id]
        except KeyError:
            folder = None

        if folder:
            can_add = checkPermission(perm, folder)
        else:
            can_add = False

        return can_add

    def canAddNews(self):
        can_add = self._checkPermInFolder('collective.nitf.AddNewsArticle',
                                          'articulos')
        return can_add

    def canManageCovers(self):
        can_manage = checkPermission('telesur.theme.coverAddable', self.context)
        return can_manage

    def canAddPolls(self):
        can_add = self._checkPermInFolder('collective.polls.AddPoll',
                                          'encuestas')
        return can_add


class AddForm(base.NullAddForm):
    """Portlet add form.
    """
    def create(self):
        return Assignment()
