from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='telesur.portlets',
      version=version,
      description="Aqui se crearan portlets a utilizar en el sitio de TeleSUR",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone :: 4.1",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
      keywords='portlets website plone teleSUR',
      author='',
      author_email='',
      url='https://github.com/desarrollotv/telesur.portlets',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['telesur'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'disqus-python==0.4.1',
      ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
