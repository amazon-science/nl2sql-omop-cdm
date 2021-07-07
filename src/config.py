from os import path as osp
from engine.step5.template_definitions import (
    get_state_name_template,
    get_concept_name_template,
)
from engine.step5.rendering_functions import (
    render_gender_template,
    render_race_template,
    render_ethnicity_template,
    render_state_template,
    render_condition_template,
    render_drug_template,
)

_current_file_dir = osp.dirname(osp.realpath(__file__))


# Step 1:
ENTITY_DETECTION_SCORE_THR = 0.7
DRUG_RELATIONSHIP_SCORE_THR = 0.7


# Step 2:


# Step 3:


# Step 4:
MODEL_PATH = "SPECIFY YOUR MODEL PATH. E.G. /home/ec2-user/SageMaker/efs/models/wikisql_pretrained_model.ckpt"

# Model maximum input and output length (for input questions and output query templates)
INPUT_MAX_LENGTH = 256
OUTPUT_MAX_LENGTH = 750


# Step 5: Render ML output
SCHEMA = "cmsdesynpuf23m"

placeholder2template = {
    "with_arg": {
        "<GENDER-TEMPLATE>": render_gender_template,
        "<RACE-TEMPLATE>": render_race_template,
        "<ETHNICITY-TEMPLATE>": render_ethnicity_template,
        "<STATEID-TEMPLATE>": render_state_template,
        "<CONDITION-TEMPLATE>": render_condition_template,
        "<DRUG-TEMPLATE>": render_drug_template,
        "<STATENAME-TEMPLATE>": render_state_template,
    },
    "with_no_arg": {
        "<GENDER-TEMPLATE>": get_concept_name_template(SCHEMA, "Gender"),
        "<RACE-TEMPLATE>": get_concept_name_template(SCHEMA, "Race"),
        "<ETHNICITY-TEMPLATE>": get_concept_name_template(SCHEMA, "Ethnicity"),
        "<STATENAME-TEMPLATE>": get_state_name_template(SCHEMA),
    },
}

# Step 6: SQL query executing
REDSHIFT_PARM = {
    "port": "SPECIFY THE PORT TO CONNECT TO REDSHIFT.",
    "database": "SPECIFY THE DATABASE NAME.",
    "cluster_id": "SPECIFY THE CLUSTER ID",
    "url": "SPECIFY THE DATA BASE URL",
    "region": "SPECIFY THE AWS REGION. E.G. us-east-1",
}
