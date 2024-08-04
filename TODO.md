- ~~Preserve extensions~~ abandonned
- ~~Achieve and document "Run and Debug" inside Docker~~
- (Add the attachment of VSC to the container to `make run-dev-env`)
- ~~Logging best practices~~
- ~~Detect and trigger error if db path is incorrect (sqlite3.connect() doesn't seem to react)~~
- ~~Download the db file (exclude it from the image like libs). Do it with sh and dockerfile~~
- ~~Naming conventions folder, files, etc. hyphen vs. dash~~
- Make streamlit app
# episodes released/tume unit
# episodes released/tume unit/hosting platform
- Understand linux root dirs


Yes, to take advantage of the copied Python libraries in the .lib folder, you need to configure your Python environment to use this folder as the Python libraries folder. You can achieve this by setting the PYTHONPATH environment variable to include the .lib directory.

Here's how you can do it:

Set the PYTHONPATH environment variable:
export PYTHONPATH=${PWD}/.lib

Run your Python script:
python your_script.py

Alternatively, you can set the PYTHONPATH directly when running the Python script:
PYTHONPATH=${PWD}/.lib python your_script.py

This will ensure that Python includes the .lib directory in its search path for modules and packages, allowing it to use the libraries copied from the Docker container.
