from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
from zope import schema

from Acquisition import aq_parent, aq_inner
from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm
from plone.app.portlets.interfaces import IPortletPermissionChecker
from z3c.form import button
from z3c.form import form, field
from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from telesur.portlets import _

from telesur.widgets.videos import AddVideosFieldWidget


class IAddVideos(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
           description=_(u"The header for the portlet. Leave empty for none."),
           required=False)

    relatedVideos = RelationList(
        title=_(u'Related Videos'),
        default=[],
        value_type=RelationChoice(title=u"Related",
                      source=ObjPathSourceBinder()),
        required=False,
        )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IAddVideos)

    header = None

    def __init__(self, header=None,):
        self.header = header

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Add videos")


class Renderer(base.Renderer, form.DisplayForm):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = template = ViewPageTemplateFile('addvideos.pt')
    fields = field.Fields(IAddVideos).omit('header')
    fields['relatedVideos'].widgetFactory = AddVideosFieldWidget

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def getAddVideosWidget(self):
        factory = self.fields['relatedVideos'].widgetFactory.get('display')
        widget = factory(self.fields['relatedVideos'].field, self.request)

        widget.name = 'relatedVideos'
        widget.id = 'relatedVideos'
        widget.context = self.context
        widget.ignoreContext = True
        widget.ignoreRequest = True
        widget.mode = 'display'
        widget.update()

        return widget.render()


class AddForm(form.AddForm):
    implements(IPortletAddForm)

    label = _(u"Configure portlet")
    #import pdb;pdb.set_trace()
    fields = field.Fields(IAddVideos).omit('relatedVideos')

    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(AddForm, self).__call__()

    def nextURL(self):
        addview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(addview))
        url = str(getMultiAdapter((context, self.request),
                                  name=u"absolute_url"))
        return url + '/@@manage-portlets'

    def create(self, data):
        return Assignment(**data)

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ''


class EditForm(form.EditForm):
    """An edit form for portlets.
    """

    implements(IPortletEditForm)

    label = _(u"Modify portlet")
    #import pdb;pdb.set_trace()
    fields = field.Fields(IAddVideos).omit('relatedVideos')

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(EditForm, self).__call__()

    def nextURL(self):
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        url = str(getMultiAdapter((context, self.request),
                                  name=u"absolute_url"))
        return url + '/@@manage-portlets'

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='apply')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = "Changes saved"
        else:
            self.status = "No changes"

        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ''
