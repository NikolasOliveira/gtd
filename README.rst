====================  =================================================================================
Tests                 |travis| |coveralls|
--------------------  ---------------------------------------------------------------------------------
Downloads             |pip dm| |pip dw| |pip dd|
--------------------  ---------------------------------------------------------------------------------
About                 |pip license| |pip wheel| |pip pyversions| |pip implem|
--------------------  ---------------------------------------------------------------------------------
Status                |version| |status|
====================  =================================================================================

About
=====

I've been using a TODO list for years in paper, inspired by the book "The Personal Software Process", by Watts S. Humprey. But I read the article `The Power of the TODO List`_, by `James Hood`_ and I decided to implement it in that way.

Basically, there are a file per day to write down 3 parts:

- In progress: This is the most important part: things to be accomplished today.
- Accomplished: things that were finished today.
- Backlog: Things to be accomplished in the future.


Why to use GTD?
---------------

Because it is very simple and easy to use. Just install it with ``pip install gtd`` and edit the current day with ``python -m gtd``. That's it.

The format is quite simple. Just the headers "In progress", "Accomplished" and "Backlog" for these tasks, and each task must start with a hyphen and space('- ').

Each day, it will copy the previous file, and:

- it will remove the 'Accomplished' section.
- it will move to the 'In progress' section the tasks from the 'Backlog' section that with a due date previous to current date.

The 'Backlog' section can have a due date, if they starts with ``[YYYY-MM-DD]``.

Example::

    In progress:
    - do cool things
    - do useful things

    Accomplished:
    - do minor stuff

    Backlog:
    - [2049-02-31] Take on the world

A Summary of the items you've accomplished for the past N days can be computed (E.g. for sync up meetings) with ``python -m gtd --sumary <number of days>``


Roadmap
-------

GTD_ is fully usable. In the near future it should be able to generate statistics and reports with the activity.




.. |travis| image:: https://img.shields.io/travis/magmax/gtd/master.svg
  :target: `Travis`_
  :alt: Travis results

.. |coveralls| image:: https://img.shields.io/coveralls/magmax/gtd.svg
  :target: `Coveralls`_
  :alt: Coveralls results_

.. |pip version| image:: https://img.shields.io/pypi/v/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Latest PyPI version

.. |pip dm| image:: https://img.shields.io/pypi/dm/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Last month downloads from pypi

.. |pip dw| image:: https://img.shields.io/pypi/dw/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Last week downloads from pypi

.. |pip dd| image:: https://img.shields.io/pypi/dd/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Yesterday downloads from pypi

.. |pip license| image:: https://img.shields.io/pypi/l/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: License

.. |pip wheel| image:: https://img.shields.io/pypi/wheel/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Wheel

.. |pip pyversions| image::  	https://img.shields.io/pypi/pyversions/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Python versions

.. |pip implem| image::  	https://img.shields.io/pypi/implementation/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Python interpreters

.. |status| image::	https://img.shields.io/pypi/status/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Status

.. |version| image:: https://img.shields.io/pypi/v/gtd.svg
    :target: https://pypi.python.org/pypi/gtd
    :alt: Status



.. _Travis: https://travis-ci.org/magmax/gtd
.. _Coveralls: https://coveralls.io/r/magmax/gtd

.. _@magmax9: https://twitter.com/magmax9
.. _GTD: https://github.com/magmax/gtd
.. _`James Hood`: http://jlhood.com
.. _`The Power of the TODO List`: http://jlhood.com/the-power-of-the-todo-list/
