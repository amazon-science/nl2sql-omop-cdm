Completion doc: Natural Language Queries to SQL Queries in the OMOP CDM
========================================================================

.. figure:: _static/merck-logo.png
   :scale: 40 %
   :align: center
   

* **Customer Division**: Merck & Co., Inc.

* **Customer location**: Kenilworth, New Jersey, USA 

* **POC start date, end date**:  February 2021 – June 2021

Overview
---------

Real-world data (RWD) are increasingly useful for healthcare providers, payors, regulators, and pharmaceutical companies to gather information and make decisions. However, the retrieval of such information requires specialized technical knowledge, resulting in delays and gaps. This work aims to increase information accessibility by creating a medical Natural Language to SQL (NL2SQL) tool that non-technical users can easily query RWD.

.. figure:: _static/problem_representation.png
   :scale: 95 %
   :align: center
   
   Business use case diagram


Objectives
----------

The high level goal of the project is to create a tool that enables researcher and healthcare specialists to query the OMOP CDM using Natural Language. PoC will be using the DeSynPUF data on OMOP CDM with approximately 23M people. 

The success criteria of this project is:

* Proof execution performance of key queries from Merck on the CMS DeSynPUF dataset (in the OMOP CDM).

The deliverables are:

* Set-up a SageMaker UI demo environment in Merck’s internal account. 
* Hand over tool to productionise → consistent with Merck pipeline
* Paper and open source dataset.
* Paper and/or blog on the tool
* Merck’s public reference 

Evaluation criteria: Given data limitations, the success will be evaluated based on the model performance on alternative ways to ask in-scope questions (seen during training) to their respective SQL query rather than its generalization capabilities to unseen questions. 

.. figure:: _static/ui.png
   :scale: 95 %
   :align: center
   
   Graphical User Interface of the PoC


Scope
------

The scope is defined by the following constraints:

* English language only
* Questions must be specific. For example, “Patients with condition and some observation criteria some number of days prior to or after initial condition” should specify the exact number of days permitted. 
* We can cohort patients by gender, year of birth, race or ethnicity.
* Concepts:
    * We will consider the following concept domains:
        * Gender
        * Race
        * Ethnicity
        * Condition
        * Drug
    * Include condition/drug concept and all its descendents during query.
    * Query only standard concepts. If a standard concept for a medication/condition can’t be found we will not consider it. [MLSL to check: For concepts, is there a relation in concept_relations to standard concept? To check with Greg: Can we assume this always?]
    * Drugs: 
        * only consider drugs (not drug products, ingredients, ... etc)
        * disambiguated into RxNorm vocabulary/ontology (standard drug vocab for OMOP). 
        * Won’t be querying dosage.
    * Conditions:
        * Disambiguated into ICD10 and then mapped to SNOMED (standard drug vocab. for OMOP)


* Users can query patients by year of birth.
* Time windows (e.g. having taking 2 drugs in less than 60 days) will only support day units.


Summary
--------

What are the key technical decisions and challenges of the project?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OMOP CDM presents a series of complexities that prevent traditional out of the shelf NL2SQL models to be applied. While we are aware of other complexities, for this PoC we are considering the following central complexities to draft a tool to address them.

1. Medical terms can be classified in multiple vocabularies/ontologies. The OMOP CDM contains a stack of vocabularies and users are not required to use concepts in a specific vocabulary.
2. OMOP contain standard and non-standard concepts. Standard concepts can be used to query other tables in the DataBase. For this PoC we will limit ourselves to query using standard concepts.
3. All medical concepts are contained on the “concept” table. They appear in the “concept_name” column and relate them to a “concept_id” which is unique across OMOP and are used across tables. The concept id is required to create queries.
4. When querying for a drug we can not only query for the general drug but also for any format of this drug (e.g. aspirin, aspirin 500g, aspirin 500g in tablets, etc.). A similar problem arises with conditions.

Three modeling approaches were drafted to overcome those complexities. The one outlined as main approach in the following section was selected based on:

* ML task simplicity: Simplicity the task for the ML model helps improve overall performance on use case.
* Generalization capabilities: The power of the ML model to convert unseen questions to unseen queries.  


What data processing decisions did the team make based on the business objectives and customer data quality, type, size?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

56 Natural Language Queries (NLQ) and their corresponding OMOP CDM were created in base of Merck's highest value queries. Alternative ways in which those can be asked were then delivered by Odysseus, a customer vendor specialized in OMOP CDM. 

What models and methodologies are the team exploring and why?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Based on literature research the team explored transformers-based models: Base BERT, T5, T5 finetunned on WikiSQL. Given the high similarity of the NLQs, we observed that all three models had similar performance. We decided to move fowrard with T5 finetunned on WikiSQL given a higher performance for out of scope questions (SQL queries not seen during training) which pointed to higher generalization power to unseen SQL queries. 

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents
   
   omop
   tool.schema
   data.creation
   model.development
   model.results
   next.steps
   modules
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`