Debugging
=========

Maintaining proper execution of DFFML API both in development and deployment levels is the top priority of the development team. DFFML modules are tightly coupled; as a result, the debugging process can be complicated. 
After identifying the potential problems or encountering an error during execution time, developers need to reproduce the problem and also be able to acquire knowledge about the program and state of the variables, specifically a couple of steps before the problems. This requires setting up a debugging environment. In the following section, setting up a debugger for DFFML in VSCode is presented. 

Setting up debugging in Visual Studio Code (VSCode)
---------------------------------------------------

`VSCode <https://code.visualstudio.com/>`_ provides powerful tools for debugging support. For this project, we use Python extension. For more details about debugging configurations for Python apps in VSCode see this `link <https://code.visualstudio.com/docs/python/debugging>`_.

If you are planning on contributing to the project, or track your debugging process, it is a better idea to have your own copy of DFFML on your Github account. 

- Log in to your Github account and go to `DFFML <https://github.com/intel/dffml>`_ repository. There is a ``Fork`` tab at the top right of the page. Click on the button to fork a copy into your Github account. 
 
- In your local computer, create a new folder for the project, open terminal (Mac and Linux) or `Gitbash <https://gitforwindows.org/>`_ (Windows) and navigate to the folder. Using the following command, clone your forked DFFML repository to this folder.

    .. code-block:: console

        git clone git@github.com:[username]/dffml.git

- Navigate inside the DFFML folder and using the following command, create a new branch to track your debugging process.

    .. code-block:: console
    
        git checkout -b [new branch name]

- You successfully set up the version controlling configurations. Now you need to install DFFML. See `Getting Set Up To Work On DFFML <https://intel.github.io/dffml/contributing/dev_env.html>`_ section for installing details in the development mode. 

- Open VSCode app, on the menu bar, click on the ``File`` then choose ``Open Folder``. Locate DFFML folder and open it. Inside the folder in VSCode, select ``setup.py`` file. This helps VSCode to retrieve your Python environment (either base or any virtual environment) that you setup. You can close the ``setup.py`` file.

- Go to the menu bar and click on the ``Run``. Choose Python from the drop-down menu and then select module. Inside the module text input field type ``dffml`` and press Enter. This will create a ``launch.json`` file under the ``.vscode`` folder.  

- It should be similar to the following:

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

- ``dffml`` module needs arguments to run. Add arguments as a key-value pair into the embedded configurations container. Here is the example ``launch.json`` file for the `Quickstart <https://intel.github.io/dffml/quickstart/model.html>`_ example.

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
                        "-model-features", "Years:int:1", "Expertise:int:1", "Trust:float:1",
                        "-model-predict", "Salary:float:1",
                        "-sources", "f=csv",
                        "-source-filename", "training.csv"
                    ]
                }
            ]
        }

- Save the file and click on the ``Run`` at the menu bar, and then click on Start Debugging. The code should run successfully to the end. You can add ``"stopOnEntry": true,`` in the configurations container to break immediatly when the program launches or you can use break point to stop at any arbitrary point in the code. 

Read more about debugging a Python code in VSCode `here <https://code.visualstudio.com/docs/python/debugging>`_.


.. The following are ways to debug issues you might run into when working on DFFML.

Potential Issues
----------------

Many times issues are because a package you are working on is not installed in
development mode. First try checking ``~/.local/lib/python3.7/site-packages/`` and
if you see anything other than ``.egg-link`` behind the name of the ``dffml``
package you are working on, you probably need to delete that package and
re-install it in development mode (``pip install -e``).

Plugin Loading / Entrypoint Issues
----------------------------------

interface, HTTP API, etc. It's probably an entry point issue.

The ``dev`` service has a helper command to help you debug issues with installed
entrypoints.

.. code-block:: console

    $ dffml service dev entrypoints list dffml.model
    tfdnnc = dffml_model_tensorflow.dnnc:DNNClassifierModel -> dffml-model-tensorflow 0.2.0 (/home/user/Documents/python/dffml/model/tensorflow)
    scratchslr = dffml_model_scratch.slr:SLR -> dffml-model-scratch 0.0.1 (/home/user/Documents/python/dffml/model/scratch)
    scikitadaboost = dffml_model_scikit.scikit_models:AdaBoostClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitdtc = dffml_model_scikit.scikit_models:DecisionTreeClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitgnb = dffml_model_scikit.scikit_models:GaussianNBModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitgpc = dffml_model_scikit.scikit_models:GaussianProcessClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitknn = dffml_model_scikit.scikit_models:KNeighborsClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitlr = dffml_model_scikit.scikit_models:LinearRegressionModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitmlp = dffml_model_scikit.scikit_models:MLPClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitqda = dffml_model_scikit.scikit_models:QuadraticDiscriminantAnalysisModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitrfc = dffml_model_scikit.scikit_models:RandomForestClassifierModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)
    scikitsvc = dffml_model_scikit.scikit_models:SVCModel -> dffml-model-scikit 0.0.1 (/home/user/Documents/python/dffml/model/scikit)

