# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility, getMultiAdapter

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from telesur.portlets import hot_threads
from telesur.portlets import popular_threads
from telesur.portlets.testing import INTEGRATION_TESTING


class PortletTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet1 = getUtility(
            IPortletType,
            name='telesur.portlets.HotThreads')
        portlet2 = getUtility(
            IPortletType,
            name='telesur.portlets.PopularThreads')

        self.assertEquals(portlet1.addview,
                          'telesur.portlets.HotThreads')

        self.assertEquals(portlet2.addview,
                          'telesur.portlets.PopularThreads')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet1 = hot_threads.Assignment(5, 'testforum')

        portlet2 = popular_threads.Assignment(5, 'interval', 'testforum',)

        self.failUnless(IPortletAssignment.providedBy(portlet1))
        self.failUnless(IPortletAssignment.providedBy(portlet2))
        self.failUnless(IPortletDataProvider.providedBy(portlet1.data))
        self.failUnless(IPortletDataProvider.providedBy(portlet2.data))

    def test_invoke_add_view(self):
        portlet1 = getUtility(
            IPortletType,
            name='telesur.portlets.HotThreads')

        portlet2 = getUtility(
            IPortletType,
            name='telesur.portlets.PopularThreads')

        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')

        for m in mapping.keys():
            del mapping[m]
        addview1 = mapping.restrictedTraverse('+/' + portlet1.addview)
        addview2 = mapping.restrictedTraverse('+/' + portlet2.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview1.createAndAdd(data={'max_results': 5,
                                    'forum': 'testforum'})

        addview2.createAndAdd(data={'max_results': 5,
                                    'interval': 'interval',
                                    'forum': 'testforum'})

        self.assertEquals(len(mapping), 2)
        self.failUnless(isinstance(mapping.values()[0],
                                   hot_threads.Assignment))

        self.failUnless(isinstance(mapping.values()[1],
                                   popular_threads.Assignment))

    def test_invoke_edit_view(self):

        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo1'] = hot_threads.Assignment(5,
                                                 'testforum')

        mapping['foo2'] = popular_threads.Assignment(5,
                                                     'interval',
                                                     'testforum',)

        editview1 = getMultiAdapter((mapping['foo1'], request), name='edit')
        editview2 = getMultiAdapter((mapping['foo2'], request), name='edit')
        self.failUnless(isinstance(editview1, hot_threads.EditForm))
        self.failUnless(isinstance(editview2, popular_threads.EditForm))

    def test_obtain_renderer(self):

        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assgmnt1 = hot_threads.Assignment(5,
                                          'testforum')

        assgmnt2 = popular_threads.Assignment(5,
                                              'interval',
                                              'testforum',)

        renderer1 = getMultiAdapter(
            (context, request, view, manager, assgmnt1), IPortletRenderer)
        renderer2 = getMultiAdapter(
            (context, request, view, manager, assgmnt2), IPortletRenderer)

        self.failUnless(isinstance(renderer1, hot_threads.Renderer))
        self.failUnless(isinstance(renderer2, popular_threads.Renderer))


class RenderTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):

        assgmnt1 = hot_threads.Assignment(5,
                                          'testforum')

        assgmnt2 = popular_threads.Assignment(5,
                                              'interval',
                                              'testforum',)

        r1 = self.renderer(context=self.portal,
                          assignment=assgmnt1)

        r2 = self.renderer(context=self.portal,
                          assignment=assgmnt2)

        r1 = r1.__of__(self.portal)
        r2 = r2.__of__(self.portal)
        r1.update()
        r2.update()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
