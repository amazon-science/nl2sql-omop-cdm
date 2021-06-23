Model Performance Results
=========================

In this POC, there are two metrics used to evaluate the model:

1. Exact-matching (Logical-form) Accuracy: 
The percentage of the predicted queries having the exact match with the ground truth queries.

2. Execution Accuracy: 
The percentage of the predicted queries, when executed, result in the correct result.

The trained model performance is summarized in the table below.

.. list-table:: Model Performance Results
   :widths: 50 25 25
   :header-rows: 1

   * - Metric
     - Validation Set
     - Test Set
   * - Exact Match
     - 0.9926
     - 0.9920
   * - Execution
     - 0.9999
     - 0.9999
     
In addition, we also tested the model against similar input questions that were provided by the customer. We could get similar results model performance.