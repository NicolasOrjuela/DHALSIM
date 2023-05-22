Testing
===========
The tests are located in the :code:`/test` folder and to run any of them simply input the command :

.. prompt:: bash $

    python3 -m pytest path/to/testfile.py -vv

Output
-------------
Once the testing is finished, a report will be shown in the terminal with every test run within the file and whether it was successful or not.
If a specific test was not successful, the report will show the line in the file where the error happened and what other files in the project were involved in the error.
