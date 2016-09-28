Style Commandments
=======================

- Tendrl's coding style is inspired by one of the largest python projects, OpenStack
  http://docs.openstack.org/developer/hacking/   (excluding the license and trademark sections)


Creating Unit Tests
-------------------
For every new feature, unit tests should be created that both test and
(implicitly) document the usage of said feature. If submitting a pull request for a
bug that had no unit test, a new passing unit test should be added. If a
submitted bug fix does have a unit test, be sure to add a new one that fails
without the patch and passes with the patch.