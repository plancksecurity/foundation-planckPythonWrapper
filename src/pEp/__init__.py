# pEp package
# This file is being exectued upon 'import pEp'
#
# __all__ could be used to limit the symbols exported when using from <pkg> import *


# Import all symbols EXCEPT the ones beginning with underscore into the current namespace
from native_pEp import *

# import the module
import native_pEp





# Executed on module import
def init():
    print("init() called")
    native_pEp._init()

# Executed when run as script
def main():
    print("I am being run as a script")

# MAIN
if __name__ == "__main__":
    main()
else:
    init()