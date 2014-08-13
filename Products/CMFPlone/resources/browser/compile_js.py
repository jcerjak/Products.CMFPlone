from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry, IJSManualResource
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFPlone.resources.browser.configjs import RequireJsView

from urlparse import urlparse
import re

optimize = """
document.getElementById('build-%s').addEventListener('click', function (evt) {

    requirejs.optimize({
        baseUrl: '.',
        paths: %s,
        shims: %s,
        include: %s,
        out: function (text) {
            document.getElementById('%s').value = text;
        }
    }, function (buildText) {
        document.getElementById('%s-debug').value = buildText;
    });
}, false);

"""

results = """
    <button id="build-{bundle}">Build it</button>
    <h2>{bundle}</h2>
    <textarea id="{bundle}"></textarea>
    <h2>Build Messages {bundle}</h2>
    <textarea id="{bundle}-debug"></textarea>
"""

class OptimizeJS(RequireJsView):

    def get_bundles(self):
        bundles = self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        return bundles

    def results(self):
        (baseUrl, paths, shims) = self.get_requirejs_config()
        resource_registry = self.registryResources()
        bundles = self.get_bundles()
        result = ""
        for key, bundle in bundles.items():
            if bundle.resource:
                if bundle.resource in resource_registry and resource_registry[bundle.resource].js:
                    result += results.format(**{'bundle': key})
        return result

    def optimize(self):
        (baseUrl, paths, shims) = self.get_requirejs_config()
        resource_registry = self.registryResources()
        bundles = self.get_bundles()
        result = ""
        for key, bundle in bundles.items():
            if bundle.resource:
                if bundle.resource in resource_registry and resource_registry[bundle.resource].js:
                    if key == 'plone_bbb':
                        # special case as it needs more includes
                        list_of_js = self.registry.records['Products.CMFPlone.jslist']
                        scripts = self.get_bbb_scripts()
                        loaded = []
                        for script_id in list_of_js.value:
                            if script_id in scripts:
                                loaded.append(script_id)
                                src = self.get_data(scripts[script_id])
                                if src:
                                    norequire.append(src)

                        # The rest of scripts
                        for key, script in scripts.items():
                            if key not in loaded:
                                src = self.get_data(script)
                                if src:
                                    norequire.append(src)
                        for nore in norequire:
                            paths += ', \'%s\': \'%s\'' % (nore, nore)
                        result += optimize % (key, paths, shims, norequire, key, key)
                    else:
                        result += optimize % (key, paths, shims, [bundle.resource], key, key)
        return result


class SaveOptimalJS(BrowserView):

    def __call__(self):
        # We need to check auth, valid js
        # TODO
        if self.request.get('text', None):
            # Save the file on the resource directory .. registry ...
            pass