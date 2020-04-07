#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-oscar-stripe-sca',
      version='0.1',
      url='https://github.com/st8st8/django-oscar-stripe-sca',
      author="Steve Bradshaw",
      author_email="steve@pcfive.co.uk",
      description="Stripe Checkout (with Payment Intents) payment module for django-oscar",
      long_description=open('README.rst').read(),
      keywords="Payment, Stripe",
      license='MIT',
      packages=find_packages(exclude=['sandbox*', 'tests*']),
      include_package_data=True,
      install_requires=[
          'django>=2',
          'django-oscar>=2',
          'stripe>=2.27.0',
      ],
      dependency_links=['https://code.stripe.com/stripe/stripe-2.27.0#egg=stripe'],
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
      ]
)
