Visual Studio Code (VSCode)
===========================

`VSCode <https://code.visualstudio.com/>`_ provides powerful tools for
debugging support. For this project, we use a Python extension. For more
details about debugging configurations for Python apps in VSCode, see this
`link <https://code.visualstudio.com/docs/python/debugging>`_.

If you are planning on contributing to the project, or track your debugging
process, it is a better idea to have your own copy of DFFML on your Github
account. For more details about setting up your git repository,
read :doc:`../git` page.

After setting up the version controlling configurations, you need to install
DFFML. See :doc:`../dev_env` page for installing details in the development mode.

Open the VSCode app, on the menu bar, click on ``File`` then choose
``Open Folder``. Locate DFFML folder and open it. Inside the folder in VSCode,
select ``setup.py`` file. This helps VSCode to retrieve your Python environment
(either base or any virtual environment) that you setup. You can close the
``setup.py`` file.

Go to the menu bar and click on ``Run``, then select ``Add configuration``.
Choose Python from the drop-down menu and then select ``module``. Inside the
module text input field type ``dffml`` and press Enter. This will create a
``launch.json`` file under the ``.vscode`` folder.

It should be similar to the following:

.. code-block:: console

    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Module",
                "type": "python",
                "request": "launch",
                "module": "dffml"
            }
        ]
    }

``dffml`` module needs arguments to run. Add arguments as a key-value pair into
the embedded configurations container. Here is the example ``launch.json`` file
for the :doc:`/quickstart/model` example.

.. code-block:: console

    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Module",
                "type": "python",
                "request": "launch",
                "module": "dffml",
                "args": [
                    "train",
                    "-model", "scikitlr",
                    "-model-features", "Years:int:1", "Expertise:int:1",
                    "Trust:float:1",
                    "-model-predict", "Salary:float:1",
                    "-sources", "f=csv",
                    "-source-filename", "training.csv"
                ]
            }
        ]
    }

Save the file and click on the ``Run`` at the menu bar, and then click on
``Start Debugging``. The code should run successfully to the end. You can add
``"stopOnEntry": true,`` in the configurations container to break immediately
when the program launches or you can use break point to stop at any arbitrary
point in the code. Read more about debugging a Python code in
VSCode `here <https://code.visualstudio.com/docs/python/debugging>`_.
