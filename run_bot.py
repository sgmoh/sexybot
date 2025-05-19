import os
import sys
import asyncio

# Change the current working directory to customerfrr
os.chdir('customerfrr')
sys.path.insert(0, os.getcwd())

# Now we can import from the main module
from main import main

if __name__ == "__main__":
    asyncio.run(main())