# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages

PACKAGE_NAME = 'churn'
PACKAGE_VERSION = '0.1'

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description="Basic per directory churn metrics for Mercurial Repo",
      long_description="TODO: Create read the docs",
      author='Mozilla Automation and Testing Team',
      author_email='tools@lists.mozilla.org',
      url='TODO Create wiki page',
      license='MPL 1.1/GPL 2.0/LGPL 2.1',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[""],
      tests_require=[''],
      platforms =['Any'],
      classifiers=['Development Status :: Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Tools',
                  ],
      entry_points={
          "console_scripts": [
              "hgchurn = churn"
          ]}
     )
