"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import logging
import psycopg2

# import boto3
import pandas as pd

import logging

logger = logging.getLogger(__name__)


def connect_to_db(redshift_parameters, user, password):
    """Connect to database and returns connection

    Args:
        redshift_parameters (dict): Redshift connection parameters.
        user (str): Redshift user required to connect.
        password (str): Password associated to the user

    Returns:
        Connection: boto3 redshift connection

    """

    try:
        conn = psycopg2.connect(
            host=redshift_parameters["url"],
            port=redshift_parameters["port"],
            user=user,
            password=password,
            database=redshift_parameters["database"],
        )

        return conn

    except psycopg2.Error:
        logger.exception("Failed to open database connection.")
        print("Failed")


def execute_query(cursor, query, limit=None):
    """Execute query

    Args:
        cursor (boto3 cursor): boto3 object pointing and with established connection to Redshift.
        query (str): SQL query.
        limit (int): Limit of rows returned by the data frame. Default to "None" for no limit

    Returns:
        pd.DataFrame: Data Frame with the query results.

    """
    try:
        cursor.execute(query)
    except:
        return None

    columns = [c.name for c in cursor.description]
    results = cursor.fetchall()
    if limit:
        results = results[:limit]

    out = pd.DataFrame(results, columns=columns)

    return out


if __name__ == "__main__":
    from __init__ import *
    import config

    sql_query = (
        "SELECT COUNT(person_id) FROM cmsdesynpuf23m.person "
        + "JOIN  ( SELECT concept_id FROM cmsdesynpuf23m.concept "
        + "WHERE concept_name='FEMALE' AND domain_id='Gender' AND "
        + "standard_concept='S' )  ON gender_concept_id=concept_id;"
    )

    conn = connect_to_db(config.REDSHIFT_PARM)
    cursor = conn.cursor()
    out_df = execute_query(cursor, sql_query, limit=5)
    conn.close()
    print(out_df)
