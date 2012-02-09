# -*- coding: utf-8 -*-
""" Funciones para acceder al API de Disqus.
"""

import json
import logging
import urllib

from urlparse import urlparse

from zope.app.component.hooks import getSite
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from telesur.portlets.config import PROJECTNAME
from telesur.registry.interfaces import IDisqusSettings

logger = logging.getLogger(PROJECTNAME)


def disqus_list_hot(forum, max_results):
    """ Obtiene un listado de los threads más recomendados.
    """
    base_url = ("https://disqus.com/api/3.0/threads/listHot.json?"
                "access_token=%s&api_key=%s&api_secret=%s&"
                "forum=%s&limit=%s")

    registry = getUtility(IRegistry)
    disqus = registry.forInterface(IDisqusSettings)
    url = base_url % (disqus.access_token,
                      disqus.app_public_key,
                      disqus.app_secret_key,
                      forum,
                      max_results)

    return get_disqus_results(url)


def disqus_list_popular(forum, max_results, interval):
    """ Obtiene un listado de los threads más populares.
    """
    base_url = ("https://disqus.com/api/3.0/threads/listPopular.json?"
                "access_token=%s&api_key=%s&api_secret=%s&"
                "forum=%s&limit=%s&interval=%s")

    registry = getUtility(IRegistry)
    disqus = registry.forInterface(IDisqusSettings)
    url = base_url % (disqus.access_token,
                      disqus.app_public_key,
                      disqus.app_secret_key,
                      forum,
                      max_results,
                      interval)

    return get_disqus_results(url)


def fileopen(filename):
    """ helper function para abrir archivos durante las pruebas.
    """
    from os.path import dirname
    return open('%s/tests/%s' % (dirname(__file__), filename))


def get_disqus_results(url):
    """ Consulta el API de Disqus utilizando el url pasado como parámetro.
    """
    # HACK: para poder hacer pruebas unitarias introducimos la posibilidad de
    # abrir url y archivos; si existe scheme, es un url; de lo contario es un
    # archivo
    url_parse = urlparse(url)
    is_url = url_parse.scheme != ''

    result = []
    try:
        if is_url:  # funcionamiento normal: abrimos el url
            request = urllib.urlopen(url)
        else:       # funcionamiento alterno: abrimos un archivo
            request = fileopen(url)
    except IOError:
        logger.error('IOError accessing %s://%s%s' % (url_parse.scheme,
                                                      url_parse.netloc,
                                                      url_parse.path))
    else:
        response = request.read()
        results = json.loads(response)

        if results['code'] != 0:
            logger.error('Disqus API error - '\
                         'code: %(code)i - response: %(response)s - '\
                         'See "http://disqus.com/api/docs/errors/" ' \
                         'for more details' % results)
        else:
            result = results['response']

    finally:
        # HACK: El API de Disqus no retorna los datos en forma correcta.
        # Este código obtiene el titulo con base en la url regresada por
        # Disqus y luego busca en el catalogo construyendo la url desde
        # el id del objeto hacia el site root. Además reemplaza la url
        # por la url usada para acceder al sitio.
        site = getSite()
        portal_catalog = getToolByName(site, 'portal_catalog')
        path = list(site.getPhysicalPath())
        items = []

        for item in result:
            parts = urlparse(item['link'])
            stack = [part for part in parts.path.split("/") if part]
            oid = None
            while stack:
                part = stack.pop()
                if not oid:
                    oid = str(part)
                path.insert(2, part)
                query = {'id': oid, 'path': {'query': "/".join(path)}}
                brains = portal_catalog.searchResults(query)
                if brains:
                    brain = brains[0]
                    if brain.Title:
                        item['title'] = brain.Title
                        item['link'] = brain.getURL()
                        items.append(item)
                    break

        return items
