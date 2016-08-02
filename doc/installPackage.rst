Install a Package
=================

Installing a Package File
-------------------------

Installing a Package by Hand
----------------------------

Unarchive the package and place it in ~/.local/share/arctool/packages or
equivalent.

Handling Package Dependencies
-----------------------------

ARCTool's default packages have already resolved their dependencies. If any
plugins only require pypandoc, then they should be okay as well. However, if a
package requires other dependencies to be installed, you'll have to handle this
yourself for now. Installing dependencies via pip3 should do the trick.