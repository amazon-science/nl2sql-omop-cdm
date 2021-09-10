"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

from os import path as osp
import sys
import getpass

sys.path.append("../")

from step1.entity_extraction import detect_entities
from step2.entity_processing import add_omop_disambiguation_options, add_placeholders
from step3.nlq_processing import replace_name_for_placeholder
from step4.model_dev.t5_inference import Inferencer
from step5.sql_processing import render_template_query
from step6.query_execution import connect_to_db, execute_query
from copy import deepcopy


class nlq2SqlTool(object):
    def __init__(self, config):
        """Initialize the nlq2SQL tool.

        Args:
            config (module): Configuration module (`./config.py`)

        Returns:
            None
        """

        self.config = config
        self.model = Inferencer(config.MODEL_PATH)

    def set_db_credentials(self, user, password):
        """Registes DB credentials and test connection.

        Args:
            user (str): DB user.
            password (str): DB password.

        Returns:
            None
        """
        self._user = user
        self._password = password

        # test connection
        test_conn = connect_to_db(self.config.REDSHIFT_PARM, self._user, self._password)
        test_conn.close()

    def clear_credentials(self):
        """Deletes the user and password data base credentials from the tool

        Args:
            None

        Returns:
            None
        """
        if self.credentials_exist():
            del self._user
            del self._password

    def credentials_exist(
        self,
    ):
        """Chceck whether or not the credentials are registred in the tool.

        Args:
            None

        Returns:
            bool: True if user and password are, False otherwise.
        """
        return hasattr(self, "_user") and hasattr(self, "_password")

    def _open_redshift_connection(
        self,
    ):
        """Open connect to the redshift database.

        Args:
            None

        Returns:
            None


        """
        self.conn = connect_to_db(self.config.REDSHIFT_PARM, self._user, self._password)

    def _close_redshift_connection(
        self,
    ):
        """Close connect to the redshift database.

        Args:
            None

        Returns:
            None

        """
        if not hasattr(self, "conn"):
            raise AttributeError("Connection has to be opened before closing it")

        self.conn.close()

    def detect_entities(self, nlq):
        """Detect entities in a Natural Language Query

        Args:
            nlq (str): Natural Language Query.

        Returns:
            dict: Dictionary of detected entities.

        """
        return detect_entities(
            nlq,
            self.config.ENTITY_DETECTION_SCORE_THR,
            self.config.DRUG_RELATIONSHIP_SCORE_THR,
        )

    def process_entities(self, entities, **kwargs):
        """Process entiteis by adding disambiguation options to match OMOP CDM terminology & assign placeholder

        Args:
            entities (dict): Dictionary of detected entities.

        Returns:
            dict: Processed entities (disambiguation options and default disambiguation).

        """
        entities = deepcopy(entities)
        #         TODO: Implement add_omop_disambiguation_options and add_placeholders
        entities = add_omop_disambiguation_options(entities)

        entities = add_placeholders(entities, **kwargs)

        return entities

    def replace_name_for_placeholder(self, nlq, entities):
        """Comment

        Args:
            nlq (str): Natural Language Query
            entities (dict): Detected and processed entities of the `nlq`.

        Returns:
            str: Generic Natural Language Query with key names replaced by placeholders.

        """
        nlq2 = replace_name_for_placeholder(nlq, entities)
        return nlq2

    def ml_call(self, nlq):
        """Maps a NLQ to a SQL query by calling the NL2SQL ML model.

        Args:
            nlq (str): Generic Natural Language Query

        Returns:
            str: Generic SQL query.

        """
        sql_query = self.model(nlq)
        return sql_query

    def render_template_query(self, generic_sql, entities):
        """Renders the generic SQL query by replacing placeholders by appropriate arguments and sub-query templates.

        Args:
            generic_sql (str): Generic SQL
            entities (dict): Detected and processed entities (same as the ones used in the `replace_name_for_placeholder` method)

        Returns:
            str: Ready-to-execute SQL query.

        """
        return render_template_query(self.config, generic_sql, entities)

    def execute_sql_query(self, sql_query):
        """Executes the ready-to-execute `sql_query` against Amazon Redshift

        Args:
            sql_query (str): Ready-to-execute `sql_query`

        Returns:
            pd.DataFrame: Table dataframe resulting from the `sql_query` execution.

        """
        self._open_redshift_connection()
        cursor = self.conn.cursor()
        out_df = execute_query(cursor, sql_query)
        self._close_redshift_connection()
        return out_df

    def __call__(self, nlq):
        """Run pipeline end to end.

        Args:
            nlq (str): Natural Language Query

        Returns:
            pd.DataFrame: Results of executing the SQL query against Amazon Redshift.


        """
        # step1: detect_entities
        entities = self.detect_entities(nlq)

        # step2: disambiguate to OMOP CDM ontology & assign placeholder
        entities = self.process_entities(entities)

        # step3: replace placeholder in nlq -> nlq2
        nlq2 = self.replace_name_for_placeholder(nlq, entities)

        # step4: execute ML to get sql
        template_sql = self.ml_call(nlq2)

        # step5: render sql query
        final_sql = self.render_template_query(template_sql, entities)

        # execute sql query
        result = self.execute_sql_query(final_sql)

        return result


if __name__ == "__main__":

    import config

    tool = nlq2SqlTool(config)

    # query = "How many people are taking Aspirin?"
    query = "Number of patients grouped by ethnicity"

    user = input("Enter Redshift Database Username: ")
    password = getpass.getpass(prompt="Enter Redshift Datbase Password: ")

    tool.set_db_credentials(user, password)

    df = tool(query)

    print("Input :", query)
    print("Output :", df)
