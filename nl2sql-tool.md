# NL2SQL Tool

## Overview

This page provides an overview of the tool design. The tool has a unique input and a unique output which are the Natural Language Query (NLQ) and the resulting table respectively. It is composed of 6 sequential steps illustrated in the figure below.

![Tool's engine diagram (click for full-size view)](images/tool_schema.png)


## NL2SQL Steps

The following are the steps required in order for a natural language query to be converted to SQL query and be executed against a given OMOP CDM database.

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


## Dataset Creation

The model takes natural language questions as inputs and SQL queries as outputs. To create a dataset, you first need to create input questions (base questions) and their corresponding output SQL queries. As a next step, the input questions are converted to question templates so that specific values will be substituted with general args. For example if the input question is:

`Number of patients of race White.`

Then it will be converted to a question template as:

`Number of patients of race <ARG-RACE><0>.`

This specifies that the value is of type `race` and `0` means that it is the first argument of such type. In the next step, for each input question template, the compressed equivalent questions with synonyms are generated. For example, the corresponding equivalent questions may look as follows:

`<SYN-ARG-number/count/counts> of <SYN-ARG-patients/people/persons/individuals/subjects> of race <ARG-RACE><0>.`

`<SYN-ARG..>` specifies that the next words or phrases (separated by `/`) are synonyms of the input question word `Number`. Other parts are also similar. Once the equivalent questions are generated for all input question templates, they will unwrapped into independent questions. Some of the corresponding unwrapped questions for the above input are as follows:

`count of people of race <ARG-RACE><0>.`
`number of persons of race <ARG-RACE><0>.`
`count of individuals of race <ARG-RACE><0>.`

For output SQL queries, once the corresponding query for each input question is generated, it will be converted to SQL query templates to replace the specific values with their templates/args. For example, the corresponding SQL query for the above input question could look like as follows:


`SELECT COUNT(DISTINCT pe1.person_id) AS number_of_patients FROM cmsdesynpuf23m.person pe1 JOIN  ( SELECT concept_id FROM cmsdesynpuf23m.concept WHERE concept_name='White' AND domain_id='Race' AND standard_concept='S' )  ON pe1.race_concept_id=concept_id;`

And the SQL query template may look like the following:

`SELECT COUNT(DISTINCT pe1.person_id) AS number_of_patients FROM <SCHEMA>.person pe1 JOIN <RACE-TEMPLATE><ARG-RACE><0> ON pe1.race_concept_id=concept_id;`

In the above case, the specific database name is replaced with `<SCHEMA>` to make it generalizable. The query part to select all races is also substitued with `<RACE-TEMPLATE>`. And finally, the specific race `White` is also replaced with its corresponding arg `<ARG-RACE><0>` which is the same as that of the input question template.

Once the unwrapped equivalent question templates and SQL query templates are generated, they are fed into the model as its inputs and outputs respectively during its training and evaluation. Sample dataset for model training is found [here](https://github.com/OHDSI/Nostos). Feel free to download it and try out the NL2SQL pipeline.

The dataset creation process is summarized in the diagram below.

![The Dataset Creation Process](images/data_creation.png)

## ML Model Development

To train/fine-tune a pretrained T5 model (E.g., WikiSQL), you first need to update the model configuration file `t5_config.py`. Especially, you need to specify the input `data_dir` and `output_dir` for input data and model output directory respectively. The model training script is located in `t5_training.py`.

Once you train the model, you can also run the inference on the whole validation and test sets and compute the model performance (exact-matching and execution accuracies). The model evaluation script is located in `t5_evaluation.py`.

You can also test trained model and run inference for a single input question. The inference script is located in `t5_inference.py`. Update the necessary information and run the script to run the inference.

The end-to-end model development process is summarized in the diagram below.

![The ML Model Development Process](images/model_dev.png)
