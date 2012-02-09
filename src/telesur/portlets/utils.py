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

    if is_url:  # funcionamiento normal: abrimos el url
        try:
            request = urllib.urlopen(url)
        except IOError:
            logger.error('IOError accessing %s://%s%s' % (url_parse.scheme,
                                                          url_parse.netloc,
                                                          url_parse.path))
    else:       # funcionamiento alterno: abrimos un archivo
        request = fileopen(url)

    response = request.read()
    disqus = json.loads(response)
    if disqus['code'] != 0:
        logger.error('Disqus API error: %s (see http://disqus.com/api/docs/errors/ '
                     'for more details)' % disqus['response'])
        return []

    site = getSite()
    items = []

    for item in disqus['response']:
        # HACK: El API de Disqus no retorna los datos en forma correcta.
        # Este código obtiene el titulo con base en la url regresada por
        # Disqus y luego busca en el catalogo construyendo la url desde
        # el id del objeto hacia el site root. Además reemplaza la url
        # por la url usada para acceder al sitio.
        if item['title'] == item['link']:
            url_parse = urlparse(item['link'])
            # necesitamos deshacernos del / inicial y convertir el path a str
            path = str(url_parse.path[1:])
            obj = site.unrestrictedTraverse(path, None)
            if obj is not None:
                item['title'] = obj.Title()
                items.append(item)
        else:
            items.append(item)

    return items
