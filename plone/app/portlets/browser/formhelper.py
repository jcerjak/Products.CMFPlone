from zope.interface import implements
from zope.component import getMultiAdapter
from zope.formlib import form

import zope.event
import zope.lifecycleevent

from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.form import named_template_adapter
from plone.app.form.validators import null_validator

from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm
 
# Add a named template form, which allows us to carry some extra information
# about the referer
_template = ViewPageTemplateFile('templates/portlets-pageform.pt')
portlets_named_template_adapter = named_template_adapter(_template)

class AddForm(form.AddFormBase):
    """A base add form for portlets.
    
    Use this for portlet assignments that require configuration before being 
    added. Assignment types that do not should use NullAddForm instead.
    
    Sub-classes should define create() and set the form_fields class variable.
    
    Notice the suble difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':
    
        def create(self, data):
            return MyAssignment(data.get('foo'))
            
    whereas the NullAddForm has no data parameter:
    
        def create(self):
            return MyAssignment()
    """
    
    implements(IPortletAddForm)
    
    form_name = _(u"Configure portlet")
    
    def referer(self):
        return self.request.form.get('referer') or self.request.get('HTTP_REFERER', '')

    def nextURL(self):
        referer = self.request.form.get('referer', None)
        if referer is not None:
            return referer
        else:
            addview = aq_parent(aq_inner(self.context))
            context = aq_parent(aq_inner(addview))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            return url + '/@@manage-portlets'
    
    @form.action("Save")
    def handle_save_action(self, action, data):
        self.createAndAdd(data)
    
    @form.action("Cancel", validator=null_validator)
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
        
class NullAddForm(BrowserView):
    """An add view that will add its content immediately, without presenting
    a form.
    
    You should subclass this for portlets that do not require any configuration
    before being added, and write a create() method that takes no parameters
    and returns the appropriate assignment instance.
    """
    
    def __call__(self):
        ob = self.create()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(ob))
        self.context.add(ob)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
    
    def nextURL(self):
        referer = self.request.get('HTTP_REFERER', None)
        if referer is not None:
            return referer
        else:
            addview = aq_parent(aq_inner(self.context))
            context = aq_parent(aq_inner(addview))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            return url + '/@@manage-portlets'
    
    def create(self):
        raise NotImplementedError("concrete classes must implement create()")
    

class EditForm(form.EditFormBase):
    """An edit form for portlets.
    """
    
    implements(IPortletEditForm)
    
    form_name = _(u"Modify portlet")
    
    def referer(self):
        return self.request.form.get('referer') or self.request.get('HTTP_REFERER', '')

    def nextURL(self):
        referer = self.request.form.get('referer', None)
        if referer is not None:
            return referer
        else:    
            portlet = aq_inner(self.context)
            context = aq_parent(portlet)
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            return url + '/@@manage-portlets'
    
    @form.action("Save", condition=form.haveInputWidgets)
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = "Changes saved"
        else:
            self.status = "No changes"
            
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
            
    @form.action("Cancel", validator=null_validator)
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''