from Products.CMFPlone.migrations.migration_util import loadMigrationProfile


def final_three01(portal):
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0final-3.0.1')
    
    return out
