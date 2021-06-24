Understanding OMOP
==================

Information from `2019 Tutorial <https://www.youtube.com/watch?v=vHMkBaHJrDA>`_ .

What is OMOP?
--------------

Different countries and regions will use different systems to classify healthcare concept ( specific drugs, a specific medications, a specific procedures, etc. ). Each of those systems used their own specific schema and tables format. This makes it extremely challenging to transfer patient’s records from one countries to another or to run analysis on data coming from different systems. 

Observational Medical Outcomes Partnership Common Data Model  (OMOP CDM) acts as an abstraction layer to harmonize the different data format allowing aggregated analysis to be much more straight forward. 

.. figure:: _static/use_diagram.png
   :scale: 76 %
   :align: center
   
   OMOP CDM provides a common data model across healthcare sources.

* *Standardized structure* to house existing vocabularies used in the public domain.
* *Compiled standards* from disparate public and private sources and some OMOP-grown concepts.
* *Dynamic dataset* - vocabulary updates regularly to keep up with evolution of the sources (e.g ~monthly for RXNorm)
* *Evolving product* - vocabulary maintenance and improvements is ongoing activity. 

Overview of OMOP CDM
---------------------

* Left (blue) - patient information and information from a visit. 
* Right (orange) - standardized vocabularies with concepts at its core and some other tables that help us map source code to reference vocabularies and give us info on metadata about the concept.

.. figure:: _static/schema.png
   :scale: 76 %
   :align: center
   
   OMOP CDM schema.

Concepts and vocabularies
--------------------------

Basic unit of vocabulary is *concept*

* *Concept* is any code comming from any vocabulary. It has associated a *concept_id* as a unique identifier in the OMOP ecosystem and the OMOP vocabulary.
* *Vocabulary* refers to the source ontologies. For example, the disease domain can be defined by the ICD10MC vocabulary  and the SNOMED vocabulary. E.g. SNOMED is a vocabulary id.
* *Domain*: Kind of concept: Visit, Condition/Meas, Cost, Gender, Race, etc.
* *Concept class*: Classification of the concept from the source ontology. E.g. “Quality Metric”, “Respiratory Disease”, “Revenue Code”, “Skin Disease”, “Branded Drug Box”, etc. Those are often more specific than domain.

A way to look at those is that Vocabulary, Domain and Concept Class are ways to group and specify concepts. Vocabulary groups them by source ontology, domain groups them by rough classifications (e.g. Visit, Cost, Condition/Measurement, etc.). Concept class is a more specific classification compared to domain (e.g. “Quality Metric”, “Respiratory Disease”, etc.).

Relationships
-------------

* *Concept in the concepts table*: All contents, contains concepts and source code (medications, drugs, procedures, etc.). 
* *Direct relationship* between concepts in concept_relationship table. E.g. if a concept is in the medication domain, we have a relationship to the ingredient and another relation to drug strength. A key relation we are interested in is the *Maps to* relationship which maps a source concept to a standard concept.
* *Multi-step hierarchical relationships* pre-processed in concept_ancestor  table: OMOP CDM keep the hierarchy coming from the source vocabulary. It is kept so when they are mapping source codes (ICD10 to SNOMED) they are keeping hierarchy (e.g. liber disease is kept when mapping from one vocab to the other).

Harmonizing
------------

They put all the formats into a common structure. For concept it looks as follows:

.. figure:: _static/concept_record.png
   :scale: 76 %
   :align: center
   
   Example concept record.

* :code:`CONCEPT_ID`: OMOP CDM ID (for use in CDM), OMOP ID, standard concept id, etc.  
* :code:`CONCEPT_NAME`: Natural Language of the concept. Description of the code.
* :code:`DOMAIN_NAME`: Defines where that record having this code has to go in the OMOP CDM. Drives the data into the right location.
* :code:`VOCABULARY_ID`: Vocabulary id it belongs to. 
* :code:`CONCEPT_CLASS_ID`: Concept Class. This can be coming from the original vocabulary or from OMOP when missing in source ontology (e.g. in RXNorm: brand product class, ingredient class, etc. ). Classification from the source ontology
* :code:`STANDARD_CONCEPT`: This flag determines where a Concept is a Standard Concept, i.e. is used in the data, a Classification Concept, or a non-standard Source Concept. The allowables values are *'S' (Standard Concept)* and *'C' (Classification Concept)*, otherwise the content is *NULL*. Flags whether or not you can use this concept id in your ETL. E.g. If I have  ICD9 code what is the corresponding concept id I need to use? 
* :code:`CONCEPT_CODE`: Code from the source vocabulary (code from SNOMED, etc. ) 
* :code:`VALID_START_DATE`: Date that the concept is introduced.
* :code:`VALID_END_DATE`: Date that the code was obsoleted. If indefinitely as of now it is set to 12/31/2099. When invalidated for replacement the concept relationship table contain the map to the new concept.
* :code:`INVALID_REASON`: If is valid (12/31/2099) then this is None. Other values are *U-updated* (concept relationships will then provide the new concept) ** and *D-deleted*.

OMOP as a Common Data Model
---------------------------

OMOP does not disambiguate concepts from vocabularies (different sources/ontologies). For example, a condition insomnia appears in ICD9, ICD10, ICD10CM, SNOMED, etc. For each of those occurrence in different vocabularies there will be a concept for insomnia, each of them having a unique concept_id. You can think about the concept table as a stack of all the entries in all data sources / ontologies. In the bar representation below each y-unit is a concept and it’s color represents the vocabulary it comes from.

.. figure:: _static/vocabularies.png
   :scale: 76 %
   :align: center
   
   Stack of vocabularies in the concept table.


Now, some of those concepts are prepared to be used on ETL procedures. Those are flagged as  “Standard concepts”. For example, SNOMED is OMOP’s reference vocabulary for Conditions. So the standard conditions concepts will be those extracted from the SNOMED vocabulary. Every other source code (code from a source ontology vocabulary) needs to be mapped to the standard concept in SNOMED in order to be robustly used for ETL transformations.

Thus, OMOP CDM harmonizes the format, don’t disambiguate records. However, the relationship table does contain mappings between equivalent concepts (via concept_id’s). Those mappings preserve hierarchy from vocabularies.

.. figure:: _static/vocabularies_relationships.png
   :scale: 76 %
   :align: center
   
   Internal vocabulary mapping respecting hierarchies.


Standard concepts
-----------------


.. figure:: _static/standard_concepts.png
   :scale: 76 %
   :align: center
   
   List of standard vocabularies by domain.


Querying concepts
------------------

Concept id is unique, concept code might be. 

.. figure:: _static/concept_id_vs_concept_code.png
   :scale: 76 %
   :align: center
   
   querying by concept_id (OMOP) vs concept_code (vocabulary)

Because the same concept code might be repeated in more than one vocabulary...

.. figure:: _static/query_by_concept_code.png
   :scale: 76 %
   :align: center
   
   Querying a concept_code returning results on 7 vocabularies.

If you know the name of a concept you can query it through the concept_name:

.. figure:: _static/query_concept_name.png
   :scale: 76 %
   :align: center
   
   Example caption.
   
This is likely to return most than one results coming from different vocabularies. *In each domain, for a specific concept name only 1 concept is standard.* In the example above for condition is row 0 with concept 313217.

















