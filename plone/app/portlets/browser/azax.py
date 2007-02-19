from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.kss.interfaces import IPloneAzaxView
from plone.app.kss.azaxview import AzaxBaseView as base

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

class PortletManagerAzax(base):
    """Opertions on portlets done using KSS
    """
    implements(IPloneAzaxView)
    
    def move_portlet_up(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        
        return self._render_column(info, viewname)
        
        
    def move_portlet_down(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        
        return self._render_column(info, viewname)
        
    def delete_portlet(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        del assignments[info['name']]
        return self._render_column(info, viewname)
                
    def _render_column(self, info, view_name):
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#portletmanager-' + info['manager'].replace('.', '-'))
        
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        view = getMultiAdapter((context, request), name=view_name)
        manager = getUtility(IPortletManager, name=info['manager'])
        
        request['key'] = info['key']
        
        renderer = getMultiAdapter((context, request, view, manager,), IPortletManagerRenderer)
        renderer.update()
        ksscore.replaceInnerHTML(selector, renderer.__of__(context).render())
        return self.render()