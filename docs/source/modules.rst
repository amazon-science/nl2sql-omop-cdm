.. indirect hyperlink targets

API docs
=========

Overview
---------

At a high-level, the code is fully contained in the :code:`src/` directory and organized as illustrated below.

.. code-block:: bash

   └── src
    ├── engine
    │   ├── step1
    │   ├── step2
    │   ├── step3
    │   ├── step4
    │   │   └── model_dev
    │   │       └── utils
    │   ├── step5
    │   └── step6
    └── ui
   
The :code:`engine` package contains the logic that powers the tool and the :code:`ui` package the Graphical User Interface bridging the engine and users.


Engine
------

The packages and modules in the :code:`engine` package are organized as described below:

.. code-block:: bash

   engine
   ├── pipeline.py
   ├── step1
   │   ├── entity_extraction.py
   │   ├── _extraction_helpers.py
   │   └── __init__.py
   ├── step2
   │   ├── disambiguation_helpers.py
   │   ├── entity_processing.py
   │   ├── gender2pattern.json
   │   ├── __init__.py
   │   ├── race2pattern.json
   │   └── state2pattern.json
   ├── step3
   │   ├── __init__.py
   │   └── nlq_processing.py
   ├── step4
   │   └── model_dev
   │       ├── __init__.py
   │       ├── t5_config.py
   │       ├── t5_evaluation.py
   │       ├── t5_inference.py
   │       ├── t5_training.py
   │       └── utils
   │           ├── callback.py
   │           ├── dataset.py
   │           ├── __init__.py
   │           ├── metrics.py
   │           └── model.py
   ├── step5
   │   ├── __init__.py
   │   ├── rendering_functions.py
   │   ├── sql_processing.py
   │   └── template_definitions.py
   └── step6
       ├── __init__.py
       └── query_execution.py

The class :code:`nlq2SqlTool` in the :code:`engine/pipeline.py` module centralizes the functionalities contained in the :code:`engine` package. Detailed documentaion of the :code:`pipeline` module can be found in :doc:`src.engine.pipeline` . The entry scripts and detailed documentation for each step package can be found below:

.. list-table:: Step packages summary
   :widths: 25 25 10 35
   :header-rows: 1

   * - Step
     - Entry point
     - Documentation
     - Functionality
   * - 1
     - :code:`entity_extraction.py`
     - :doc:`src.engine.step1`
     - Entity detection
   * - 2
     - :code:`entity_processing.py`
     - :doc:`src.engine.step2`
     - Entity processing
   * - 3
     - :code:`nlq_processing.py`
     - :doc:`src.engine.step3`
     - NLQ pre-processing
   * - 4
     - :code:`model_dev.t5_inference.py`
     - :doc:`src.engine.step4`
     - NLQ to SQL ML model
   * - 5
     - :code:`sql_processing.py`
     - :doc:`src.engine.step5`
     - SQL post-processing
   * - 6
     - :code:`query_execution.py`
     - :doc:`src.engine.step6`
     - SQL execution
     

Entry points functions can be found in the :code:`pipeline` script imports.

UI
----

The modules in the :code:`engine` package are organized as described below:

.. code-block:: bash

   ui
   ├── detection_visualizer.py
   ├── __init__.py
   ├── layouts.py
   └── ui.py

The :code:`UI` class in the :code:`ui` module is the entry point of the package. Detailed documentaion of the :code:`ui` module can be found in :doc:`src.ui`. 

The :code:`layouts` module contain the aspect ratio of the UI layers. The :code:`detectiion_visualizer` module contains the logic to highlight detected entites in the UI. 


API
----

.. toctree::
   :maxdepth: 4
   :caption: API docs

   src
