# -*- coding: utf-8 -*-
from plone.portlets.interfaces import IPortletManager

class IPorletManagerLatest(IPortletManager):
    """ Manager to show the latest_nitf portlet.
        This made more easy to cache the different portlets as separated parts
        and use ESI in the varnish cache.
    """
