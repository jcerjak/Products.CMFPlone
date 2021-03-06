# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IMarkupSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getAdapter


class MarkupControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IMarkupSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IMarkupSchema))

    def test_get_default_type(self):
#        import pdb; pdb.set_trace()
        self.settings.default_type = 'text/plain'
        self.assertEquals(
            getAdapter(self.portal, IMarkupSchema).default_type,
            'text/plain'
        )

    def test_set_default_type(self):
#        import pdb; pdb.set_trace()
        getAdapter(self.portal, IMarkupSchema).default_type = 'text/plain'  # noqa
        self.assertEquals(
            self.settings.default_type,
            'text/plain'
        )

    def test_get_allowed_types(self):
        self.settings.allowed_types = ('text/plain', 'text/x-web-textile')
#        import pdb; pdb.set_trace()
        self.assertEquals(
            getAdapter(self.portal, IMarkupSchema).allowed_types,
            ('text/plain', 'text/x-web-textile')
        )

    def test_set_allowed_types(self):
#        import pdb; pdb.set_trace()
        getAdapter(self.portal, IMarkupSchema).allowed_types =\
            ('text/plain', 'text/x-web-textile')
        self.assertEquals(
            self.settings.allowed_types,
            ('text/plain', 'text/x-web-textile')
        )
