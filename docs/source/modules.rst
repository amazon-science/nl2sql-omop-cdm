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
   │   ├── nlq_processing.py
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



UI
----



Overview
---------

.. toctree::
   :maxdepth: 4
   :caption: API docs

   src
