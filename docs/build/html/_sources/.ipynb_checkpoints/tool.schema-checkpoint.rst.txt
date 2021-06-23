Tool overview
=============

This page provides an overview of the tool design. The tool has a unique input and a unique output which are the Natural Language Query (NLQ) and the resulting table respectively. It is composed of 6 sequential steps illustrated in the figure below.


.. figure:: _static/tool_schema.png
   :scale: 20 %
   :align: center
   
   Tool's engine diagram (click for full-size view)


Steps
------

**Step 1: Entity Detection**
* *Input*: Original NLQ
* *Output*: First entity dictionary. Keys are categories and values are detected names and position in NLQ.
* *Description*: Analyzes the NLQ to detect and classify the names corresponding to "TIMEDAYS", "TIMEYEARS", "DRUG", "CONDITION", "STATE", "GENDER", "ETHNICITY", "RACE".

**Step 2: Entity Processing**
* *Input*: First entity dictionary
* *Output*: Second entity dictionary
* *Description*: Expands the first entity dictionary to include "Options", "Query-arg" and "Placeholder" fields defining disambiguating options, assigned disambiguation and name placeholder for the generic NLQ respectively.

**Step 3: NLQ pre-processing**
* *Input*: Original NLQ & second entity dictionary
* *Output*: Generic NLQ
* *Description*: Name detected in the original NLQ are replaced for their placeholders using the information in second entity dictionary. 

**Step 4: NLQ to SQL ML model**
* *Input*: Generic NLQ
* *Output*: Generic SQL query
* *Description*: Maps a generic NLQ to a generic SQL query using Machine Learning.

**Step 5: SQL post-processing**
* *Input*: Generic SQL query (& pre-defined sub-query templates)
* *Output*: Executable SQL query
* *Description*: Renders the generic value by replacing template placeholders in the generic SQL query by their pre-defined sub-queries and the arguments placeholder by their corresponding "Query-arg" parameter in the Second entity dictionary.

**Step 6: SQL execution**
* *Input*: Executable SQL query
* *Output*: Table 
* *Description*: Executes the SQL query against the DataBase to return the information requested by the user. 
