==============
Version-Differ
==============


.. image:: https://img.shields.io/pypi/v/version_differ.svg
        :target: https://pypi.python.org/pypi/version_differ

.. image:: https://img.shields.io/travis/nasifimtiazohi/version_differ.svg
        :target: https://travis-ci.com/nasifimtiazohi/version_differ

.. image:: https://readthedocs.org/projects/version-differ/badge/?version=latest
        :target: https://version-differ.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/nasifimtiazohi/version_differ/shield.svg
     :target: https://pyup.io/repos/github/nasifimtiazohi/version_differ/
     :alt: Updates



Accurate diffing between two versions of a package


* Free software: MIT license
* Documentation: https://version-differ.readthedocs.io.


Features
--------

* Covers eight ecosystems, namely Cargo, Composer, Go, Maven, npm, NuGet, pip, and RubyGems
* Given any two version of a package, returns the list of changed files with the count of loc_added and loc_removed in each file
* For Cargo, Composer, Maven, npm, pip, and RubyGems, version-differ downloads source code for a package:version directly from respective package registries to measure git-diff
* For Go and NuGet, it clones the source code repository, apply some heuristics to detect package specific files, and measures git-diff

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
