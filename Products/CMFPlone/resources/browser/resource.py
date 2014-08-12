from Acquisition import aq_inner, aq_base, aq_parent
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import (
    IBundleRegistry, IResourceRegistry)
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class ResourceView(ViewletBase):
    """ Information for script rendering. """

    def evaluateExpression(self, expression, context):
        """Evaluate an object's TALES condition to see if it should be
        displayed.
        """
        try:
            if expression.text and context is not None:
                portal = getToolByName(context, 'portal_url').getPortalObject()

                # Find folder (code courtesy of CMFCore.ActionsTool)
                if context is None or not hasattr(context, 'aq_base'):
                    folder = portal
                else:
                    folder = context
                    # Search up the containment hierarchy until we find an
                    # object that claims it's PrincipiaFolderish.
                    while folder is not None:
                        if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                            # found it.
                            break
                        else:
                            folder = aq_parent(aq_inner(folder))

                __traceback_info__ = (folder, portal, context, expression)
                ec = createExprContext(folder, portal, context)
                # add 'context' as an alias for 'object'
                ec.setGlobal('context', context)
                return expression(ec)
            else:
                return True
        except AttributeError:
            return True

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.registry = getUtility(IRegistry)

    def get_bundles(self):
        return self.registry.collectionOfInterface(
            IBundleRegistry, prefix="Products.CMFPlone.bundles")

    def get_resources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry, prefix="Products.CMFPlone.resources")

    def development(self):
        return self.registry.records['Products.CMFPlone.resources.development']

    def bundles(self):
        bundles = self.get_bundles()
        for key, bundle in bundles.items():
            if bundle.enabled:
                # check expression
                if bundle.expression:
                    if bundle.cooked_expression:
                        expr = Expression(bundle.expression)
                        bundle.cooked_expression = expr
                    if self.evaluateExpression(bundle.cooked_expression,
                                               self.context):
                        continue
                yield key, bundle

    def ordered_result(self):
        result = []
        # The first one
        inserted = []
        depends_on = {}
        for key, bundle in self.bundles():
            if bundle.depends is None or bundle.depends == '':
                # its the first one
                self.get_data(bundle, result)
                inserted.append(key)
            else:
                name = bundle.depends.strip()
                if name in depends_on:
                    depends_on[name].append(bundle)
                else:
                    depends_on[name] = [bundle]

        while len(depends_on) > 0:
            found = False
            for key, bundles_to_add in depends_on.items():
                if key in inserted:
                    found = True
                    for bundle in bundles_to_add:
                        self.get_data(bundle, result)
                        inserted.append(key)
                    del depends_on[key]
            if not found:
                continue

        # THe ones that does not get the dependencies
        for bundle in depends_on.values():
            self.get_data(bundle, result)

        return result