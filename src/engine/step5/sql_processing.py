"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import re
import config

SCHEMA_P = re.compile("<SCHEMA>")

# template-based placeholders
PLACE_HOLDER_P = re.compile("<\w*-TEMPLATE><ARG-\w*><\d+>")
PLACE_HOLDER_META_P = re.compile("(<\w*-TEMPLATE>)<ARG-(\w*)><(\d+)>")

# non template-based placeholders
ARG_PLACE_HOLDER_P = re.compile("<ARG-\w*><\d+>")
ARG_PLACE_HOLDER_META_P = re.compile("<ARG-(\w*)><(\d+)>")

# non template-based placeholders
TEMPLATE_PLACE_HOLDER_P = re.compile("<\w*-TEMPLATE>")


def render_template_query(config, general_query, args_dict):
    """Main function of the step. Renders a general SQL query with arguments placeholders and
    template placeholders with their corresponding values and subqueries respectively.


    Args:
        config (module): General tool configuration.
        general_query (str): General SQL query.
        args_dict (dict): Dictionary of processed arguments from step 2.

    Returns:
        str: Rendered query by replacing argument and template placeholders.
    """

    # Render <SCHEMA> placeholder
    current_query = re.sub(SCHEMA_P, config.SCHEMA, general_query)

    # Render "<\w*-TEMPLATE><ARG-\w*><\d+>" placeholders. E.g. descendent templates.
    item = re.search(PLACE_HOLDER_P, current_query)
    placeholder2templates = config.placeholder2template["with_arg"]
    while item:

        start, end = item.start(0), item.end(0)
        place_holder = current_query[start:end]

        # extract metadta from placeholder
        template_type, domain, idx = re.findall(PLACE_HOLDER_META_P, place_holder)[0]

        # retrieve concept name
        idx = int(idx)
        concept_name = args_dict[domain][idx]["Query-arg"]

        # retrieve rendered sub-query
        if template_type not in placeholder2templates.keys():
            item = ""
            continue
        sub_query = placeholder2templates[template_type](config.SCHEMA, concept_name)

        # replace in current query
        current_query = current_query[:start] + sub_query + current_query[end:]

        # search for next placeholder
        item = re.search(PLACE_HOLDER_P, current_query)

    # Render "<ARG-\w*><\d+>" placeholders. E.g. days.
    item = re.search(ARG_PLACE_HOLDER_P, current_query)
    while item:

        start, end = item.start(0), item.end(0)
        place_holder = current_query[start:end]

        # extract metadta from placeholder
        domain, idx = re.findall(ARG_PLACE_HOLDER_META_P, place_holder)[0]

        # retrieve argument value
        idx = int(idx)
        arg_value = args_dict[domain][idx]["Query-arg"]

        # replace argument value in current-query
        current_query = current_query[:start] + arg_value + current_query[end:]

        # search for next placeholder
        item = re.search(ARG_PLACE_HOLDER_P, current_query)

    # Render "<\w*-TEMPLATE>" placeholders. E.g. Location names
    item = re.search(TEMPLATE_PLACE_HOLDER_P, current_query)
    placeholder2templates = config.placeholder2template["with_no_arg"]
    while item:

        start, end = item.start(0), item.end(0)
        place_holder = current_query[start:end]

        # extract metadata from placeholder
        if place_holder not in placeholder2templates.keys():
            item = ""
            continue
        sub_query = placeholder2templates[place_holder]

        # replace argument value in current-query
        current_query = current_query[:start] + sub_query + current_query[end:]

        # search for next placeholder
        item = re.search(TEMPLATE_PLACE_HOLDER_P, current_query)

    return current_query
