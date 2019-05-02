#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-oscar-stripe-sandbox',
      version='0.1',
      url='https://github.com/tangentlabs/django-oscar-stripe',
      author="David Winterbottom",
      author_email="david.winterbottom@tangentlabs.co.uk",
      description="Sandbox app - Stripe payment module for django-oscar",
      keywords="Payment, Stripe",
      license='BSD',
      include_package_data=True,
      install_requires=[
          'django-oscar>=0.6',
          'stripe==1.12.0',
           # Haystack currently expects an older version (2017-11-18)
           # sandbox settings currently setup for older versions
           'Django>=1.11.19',
      ],
      dependency_links=['https://code.stripe.com/stripe/stripe-1.12.0#egg=stripe'],
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Unix',
          'Programming Language :: Python']
      )
