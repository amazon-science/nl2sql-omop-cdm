Dataset Creation
================
The model takes natural language questions as inputs and SQL queries as outputs. To create a dataset, you first need to create input questions (base questions) and their corresponding output SQL queries. As a next step, the input questions are converted to question templates so that specific values will be substituted with general args. For example if the input question is:

.. code-block:: none

   Number of patients of race White.
   

Then it will be converted to a question template as:

.. code-block:: none

   Number of patients of race <ARG-RACE><0>.


This specifies that the value is of type `race` and `0` means that it is the first argument of such type. In the next step, for each input question template, the compressed equivalent questions with synonyms are generated. For example, the corresponding equivalent questions may look as follows:

.. code-block:: none

   <SYN-ARG-number/count/counts> of <SYN-ARG-patients/people/persons/individuals/subjects> of race <ARG-RACE><0>.


`<SYN-ARG..>` specifies that the next words or phrases (separated by `/`) are synonyms of the input question word `Number`. Other parts are also similar. Once the equivalent questions are generated for all input question templates, they will unwrapped into independent questions. Some of the corresponding unwrapped questions for the above input are as follows:

.. code-block:: none

   count of people of race <ARG-RACE><0>.
   number of persons of race <ARG-RACE><0>.
   count of individuals of race <ARG-RACE><0>.


For output SQL queries, once the corresponding query for each input question is generated, it will be converted to SQL query templates to replace the specific values with their templates/args. For example, the corresponding SQL query for the above input question could look like as follows:

.. code-block:: none

   SELECT COUNT(DISTINCT pe1.person_id) AS number_of_patients FROM cmsdesynpuf23m.person pe1 JOIN  ( SELECT concept_id FROM cmsdesynpuf23m.concept WHERE concept_name='White' AND domain_id='Race' AND standard_concept='S' )  ON pe1.race_concept_id=concept_id;


And the SQL query template may look like the following:

.. code-block:: none

   SELECT COUNT(DISTINCT pe1.person_id) AS number_of_patients FROM <SCHEMA>.person pe1 JOIN <RACE-TEMPLATE><ARG-RACE><0> ON pe1.race_concept_id=concept_id;


In the above case, the specific database name is replaced with `<SCHEMA>` to make it generalizable. The query part to select all races is also substitued with `<RACE-TEMPLATE>`. And finally, the specific race `White` is also replaced with its corresponding arg `<ARG-RACE><0>` which is the same as that of the input question template.

Once the unwrapped equivalent question templates and SQL query templates are generated, they are fed into the model as its inputs and outputs respectively during its training and evaluation.

The dataset creation process is summarized in the diagram below.

.. figure:: _static/data_creation.png
   :scale: 70 %
   :align: center
   
   The Dataset Creation Process.


Dataset Size
============
The dataset size used in the POC is shown below:

.. list-table:: Dataset Size
   :widths: 50 50
   :header-rows: 1

   * - Question Types
     - Total
   * - Base Questions
     - 56
   * - Equivalent Questions(Wrapped)
     - 789
   * - Equivalent Questions(Unwrapped)
     - 799,260
