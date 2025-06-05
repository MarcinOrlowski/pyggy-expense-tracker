# Test Documentation with Broken Links

This documentation file contains some broken links to test the error handling.

## Working Links

- [Getting Started](GETTING_STARTED) - This should work
- [Docker Setup](DOCKER) - This should work too

## Broken Links

- [Non-existent Page](nonexistent_page) - This will show a user-friendly error
- [Another Broken Link](missing_documentation) - This will also show an error

## Features

The error handling should:

1. Show a user-friendly error message instead of Django's debug page
2. Provide navigation back to the help index
3. Include helpful action buttons
4. Display proper styling with icons

Test the broken links above to see the error handling in action!
