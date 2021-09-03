"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import sys
import os
from os import path as osp

current_folder = osp.dirname(osp.abspath(__file__))
sys.path.append(current_folder)

import ipywidgets as widgets
from IPython.core.display import display, HTML
import re
from copy import deepcopy
import pandas as pd
import json
import datetime
import layouts
from detection_visualizer import (
    renderer,
    prepare_visualization_input_for_raw_entities,
    prepare_visualization_input_for_processed_entities,
)

# create logs folder if it does not exist
if not osp.exists(".logs"):
    os.makedirs(".logs")


class UI(object):
    def __init__(self, tool):
        """Stores underlying tool to be used and initialize the GUI widgets.

        Args:
            tool (nlq2SqlTool): Instantiation of the Natural Language to SQL tool.

        Returns:
            None

        """

        self.tool = tool
        self._initialize_widgets()

    def main(self):
        """Method to layout and start the UI in a SageMaker Notebook.

        Args:
            None

        Returns:
            None

        """
        display(self.ui_sections)

    def _initialize_widgets(self):
        """Initialize all the UI widgets.

        Args:
            None

        Returns:
            None

        """
        # initialize UI vertical sections
        self._initialize_credentials_vsection()
        self._initialize_genearl_input_vsection()
        self._initialize_general_output_vsection()
        self._initialize_feedback_vsection()

        # combine
        self.ui_sections = widgets.VBox(
            [
                self.credentials_vsection,
                self.genearl_input_vsection,
                self.general_output_vsection,
                self.feedback_vsection,
            ],
            layout=layouts.MAIN_BOX_LAYOUT,
        )

    def _initialize_credentials_vsection(self):
        """Initialize the widgets of the credentials vertical section.

        Args:
            None

        Returns:
            None

        """

        # initialize widgets
        self.widget_db_user = widgets.Text(description="User:", layout={"width": "30%"})

        self.widget_db_password = widgets.Password(
            description="Password:", layout={"width": "30%"}
        )

        self.white_space1 = widgets.Output(layout={"width": "25%"})

        self.set_credentials_button = widgets.Button(description="Set Data Credentials")
        self.set_credentials_button.on_click(self._button_helper_record_db_credentials)

        # combine
        self._credentials_vsection = widgets.HBox(
            [
                self.widget_db_user,
                self.widget_db_password,
                self.white_space1,
                self.set_credentials_button,
            ]
        )
        self.credentials_vsection = widgets.Accordion(
            children=[self._credentials_vsection]
        )
        self.credentials_vsection.set_title(0, "DB Credentials")

    def _initialize_genearl_input_vsection(self):
        """Initialize the widgets of the general input vertical section.

        Args:
            None

        Returns:
            None

        """

        # initialize tabs
        self._initialize_main_input_tab()
        self._initialize_detection_correction_tab()
        self._initialize_disambiguation_correction_tab()

        # combine
        self.genearl_input_vsection = widgets.Tab(layout=layouts.MAIN_INTERFACE_LAYOUT)

        children = [
            self.main_input_tab,
            self.detection_correction_tab,
            self.disambiguation_correction_tab,
        ]
        self.genearl_input_vsection.children = children

        self.genearl_input_vsection.set_title(0, "Main")
        self.genearl_input_vsection.set_title(1, "Correct detection")
        self.genearl_input_vsection.set_title(2, "Correct code map")

    def _initialize_general_output_vsection(self):
        """Initialize the widgets of the general output vertical section.

        Args:
            None

        Returns:
            None

        """

        self.general_output_vsection = widgets.Output(
            layout=layouts.MAIN_DISPLAY_LAYOUT
        )

    def _initialize_feedback_vsection(self):
        """Initialize the widgets of the feedback vertical section.

        Args:
            None

        Returns:
            None

        """

        self.clear_output_button = widgets.Button(description="Clear Output")
        self.clear_output_button.on_click(self._button_helper_clear_output)

        self.clear_credentials_button = widgets.Button(description="Forget Credentials")
        self.clear_credentials_button.on_click(self._button_helper_clear_credentials)

        self.processing_flag = widgets.Output(layout={"width": "30%"})

        self.feedback_options = widgets.RadioButtons(
            value="Successful",
            options=["Successful", "Unsuccessful"],
            description="Feedback:",
            layout={"width": "25%"},
        )

        self.submit_button = widgets.Button(description="Submit feedback")
        self.submit_button.on_click(self._button_helper_log_feedback)

        self.feedback_vsection = widgets.HBox(
            [
                self.clear_output_button,
                self.clear_credentials_button,
                self.processing_flag,
                self.feedback_options,
                self.submit_button,
            ],
            layout=layouts.MAIN_FEEDBACK_LAYOUT,
        )

    def _initialize_main_input_tab(self):
        """Initialize the widgets of the main input tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """

        self.input_box = widgets.Textarea(
            placeholder="e.g. Number of patients taking Aspirin",
            description="Query:",
            layout=layouts.INPUT_TEXT_LAYOUT,
            disabled=False,
        )
        self.detect_button = widgets.Button(description="Detect")
        self.detect_button.on_click(self._button_helper_detect_button)
        self.execute_button = widgets.Button(description="Execute")
        self.execute_button.on_click(self._button_helper_execute_button)

        self.main_buttons = widgets.HBox([self.detect_button, self.execute_button])
        self.main_input_tab = widgets.VBox(
            [self.input_box, self.main_buttons], layout=layouts.INPUT_BOX_LAYOUT
        )

    def _initialize_detection_correction_tab(self):
        """Initialize the widgets of the detection correction tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """

        self.add_sub_title_1 = widgets.Output()
        self.add_sub_title_1.append_stdout("Add detection")

        self.add_name = widgets.Text(
            placeholder="Aspirin 30Mg", description="Write name", disabled=False
        )
        self.add_category = widgets.Dropdown(
            placeholder="Choose entity",
            options=[
                "DRUG",
                "CONDITION",
                "AGE",
                "STATE",
                "ETHNICITY",
                "RACE",
                "TIMEDAYS",
                "TIMEYEARS",
                "GENDER",
            ],
            description="Category:",
            ensure_option=True,
            disabled=False,
        )
        self.add_button = widgets.Button(description="Highlight")
        self.add_button.on_click(self._button_helper_record_name)

        self.add_box = widgets.HBox(
            [self.add_name, self.add_category, self.add_button],
            layout=layouts.SUB_DETECT_BOX_LAYOUT,
        )

        self.remove_sub_title_2 = widgets.Output()
        self.remove_sub_title_2.append_stdout("Remove detection")

        self.remove_name = widgets.Dropdown(
            placeholder="",
            options=[],
            description="Name:",
            ensure_option=True,
            disabled=False,
        )
        self.remove_button = widgets.Button(description="Remove")
        self.remove_button.on_click(self._button_helper_remove_name)

        self.remove_box = widgets.HBox(
            [self.remove_name, self.remove_button], layout=layouts.SUB_DETECT_BOX_LAYOUT
        )

        self.detection_correction_tab = widgets.VBox(
            [
                self.add_sub_title_1,
                self.add_box,
                self.remove_sub_title_2,
                self.remove_box,
            ],
            layout=layouts.DETECT_BOX_LAYOUT,
        )

    def _initialize_disambiguation_correction_tab(self):
        """Initialize the widgets of the disambiguation correction tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """

        # initialize widgets
        self._initialize_drug_disambiguation_correction_widgets()
        self._initialize_condition_disambiguation_correction_widgets()
        self._initialize_disambiguation_info_output_widget()

        # combine
        self._mapped_drug_box = widgets.HBox(
            [
                self.mapped_drug_category,
                self.mapped_drug_button,
                self.mapped_update_drug_text,
                self.mapped_update_drug_button,
            ]
        )
        self._mapped_condition_box = widgets.HBox(
            [
                self.mapped_condition_category,
                self.mapped_condition_button,
                self.mapped_update_condition_text,
                self.mapped_update_condition_button,
            ]
        )
        self.disambiguation_correction_tab = widgets.VBox(
            [
                self._mapped_drug_box,
                self._mapped_condition_box,
                self.disambiguation_info_output,
            ],
            layout=layouts.INFO_BOX_LAYOUT,
        )

    def _initialize_drug_disambiguation_correction_widgets(self):
        """Initialize the widgets of the drug disambiguation correction
        in the disambiguation correction tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """
        drugs = (
            [d["Text"] for d in self.entities["DRUG"]]
            if hasattr(self, "entities")
            else []
        )
        self.mapped_drug_category = widgets.Dropdown(
            placeholder="e.g. Aspirin",
            options=drugs,
            description="Drug",
            ensure_option=True,
            disabled=False,
        )
        self.mapped_drug_button = widgets.Button(description="Show drug info")
        self.mapped_drug_button.on_click(self._button_helper_drug_info)
        self.mapped_update_drug_text = widgets.Text(
            placeholder="RxNorm code", description="Map to", disabled=False
        )
        self.mapped_update_drug_button = widgets.Button(description="Update drug")
        self.mapped_update_drug_button.on_click(self._button_helper_drug_update)

    def _initialize_condition_disambiguation_correction_widgets(self):
        """Initialize the widgets of the condition disambiguation correction
        in the disambiguation correction tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """
        conditions = (
            [d["Text"] for d in self.entities["CONDITION"]]
            if hasattr(self, "entities")
            else []
        )
        self.mapped_condition_category = widgets.Dropdown(
            placeholder="e.g. Insomnia",
            options=conditions,
            description="Condition",
            ensure_option=True,
            disabled=False,
        )
        self.mapped_condition_button = widgets.Button(description="Show condition info")
        self.mapped_condition_button.on_click(self._button_helper_condition_info)
        self.mapped_update_condition_text = widgets.Text(
            placeholder="ICD10 code", description="Map to", disabled=False
        )
        self.mapped_update_condition_button = widgets.Button(
            description="Update condition"
        )
        self.mapped_update_condition_button.on_click(
            self._button_helper_condition_update
        )

    def _initialize_disambiguation_info_output_widget(self):
        """Initialize the widgets of the disambiguation correction info output
        in the disambiguation correction tab in the general input vertical section.

        Args:
            None

        Returns:
            None

        """
        self.disambiguation_info_output = widgets.Output(
            layout={"border": "1px solid black"}
        )

    def _button_helper_clear_output(self, b):
        """Helper method defining the button's action to clear the outputs.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        self.general_output_vsection.clear_output()
        self.disambiguation_info_output.clear_output()

    def _button_helper_log_feedback(self, b):
        """Helper method defining the button's action to log the feedback.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """

        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        record = {
            "time": now,
            "input": self.nlq,
            "args original": self.original_proc_entities,
            "args corrected": self.proc_entities,
            "correct": True if self.feedback_options.value == "Successful" else False,
        }

        file_path = osp.join(".logs", now + ".txt")
        with open(file_path, "a") as fp:
            json.dump(record, fp)

    def _button_helper_clear_credentials(self, b):
        """Helper method defining the button's action to clear the credentials.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        self.tool.clear_credentials()
        self.widget_db_user.value = ""
        self.widget_db_password.value = ""
        self.white_space1.clear_output()

    def _button_helper_record_db_credentials(self, b):
        """Helper method defining the button's action to record the DB credentials.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        self.white_space1.clear_output()
        try:
            db_user = self.widget_db_user.value
            db_password = self.widget_db_password.value
            self.tool.set_db_credentials(db_user, db_password)
            with self.white_space1:
                print("✅ Credentials successfully recorded")
        except:
            with self.white_space1:
                print(
                    "⛔️ Unable to access the DB. Make sure your credentials are correct"
                )

    def _button_helper_detect_button(self, b):
        """Helper method defining the button's action to detect the entities in the input NLQ.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        self.nlq = self.input_box.value
        self.entities = self.tool.detect_entities(self.nlq)
        self.proc_entities = self.tool.process_entities(self.entities)
        self.original_proc_entities = deepcopy(self.proc_entities)

        self._display_main()
        self._update_options()

    def _button_helper_execute_button(self, b):
        """Helper method defining the button's action to triggers the ML model prediction
        and execute the SQL query.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        if self.tool.credentials_exist():

            with self.processing_flag:
                print("🕝 Processing ....")

            nlq_w_placeholders = self.tool.replace_name_for_placeholder(
                self.nlq, self.proc_entities
            )
            sql_query = self.tool.ml_call(nlq_w_placeholders)

            try:
                rendered_sql_query = self.tool.render_template_query(
                    sql_query, self.proc_entities
                )
            except:
                rendered_sql_query = None

            try:
                output = self.tool.execute_sql_query(rendered_sql_query)
            except:
                output = "\n•An error ocurred. We apologise for the inconvenience. Please try to re-formulate your query."

        else:
            output = "\n⛔️ Please set your data credentials to execute the query."

        self._display_main(output, sql_query, rendered_sql_query)

        self.processing_flag.clear_output()

    def _button_helper_record_name(self, b):
        """Helper method defining the button's action to manually detect a name (highlight).

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        name = self.add_name.value
        category = self.add_category.value

        p = re.compile(f"(?i)\\b{name}\\b")

        # current entities set
        current_names = set([d["Text"] for d in self.entities[category]])
        if name not in current_names:
            for match in re.finditer(p, self.nlq):
                detected_entity = {
                    "BeginOffset": match.start(),
                    "EndOffset": match.end(),
                    "Text": name,
                }

                # add to raw entities
                self.entities[category].append(deepcopy(detected_entity))

                # process & add to proc entities
                placeholder_idx_strat = {category: len(self.proc_entities[category])}
                proc_detected_entity = self.tool.process_entities(
                    {category: [deepcopy(detected_entity)]},
                    start_indices=placeholder_idx_strat,
                )
                self.proc_entities[category].append(proc_detected_entity[category][0])
        self._display_main()
        self._update_options()

    def _button_helper_remove_name(self, b):
        """Helper method defining the button's action to manually remove a detection.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        # do removing
        remove_name_category = self.remove_name.value
        name, category = remove_name_category.split(" (category: ")
        category = category[:-1]

        # remove from entities
        for i in range(len(self.entities[category])):
            if self.entities[category][i]["Text"] == name:
                del self.entities[category][i]
                break

        # remove from proc_entities
        for i in range(len(self.proc_entities[category])):
            if self.proc_entities[category][i]["Text"] == name:
                del self.proc_entities[category][i]
                break

        self._display_main()
        self._update_options()

    def _button_helper_drug_info(self, b):
        """Helper method defining the button's action to visualize information on drug disambiguation option.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        if hasattr(self, "nlq"):
            self._visualize_drug_info()
        else:
            self._triger_no_input_warning()

    def _button_helper_condition_info(self, b):
        """Helper method defining the button's action to visualize information on condition disambiguation option.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        if hasattr(self, "nlq"):
            self._visualize_condition_info()
        else:
            self._triger_no_input_warning()

    def _button_helper_drug_update(self, b):
        """Helper method defining the button's action to manually update the disambiguation mapping of a drug.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        if hasattr(self, "nlq"):
            for d in self.proc_entities["DRUG"]:
                if d["Text"] == self.mapped_drug_category.value:
                    d["Query-arg"] = self.mapped_update_drug_text.value
                    break

            self._visualize_drug_info()
            self._display_main()
        else:
            self._triger_no_input_warning()

    def _button_helper_condition_update(self, b):
        """Helper method defining the button's action to manually update the disambiguation mapping of a condition.

        Args:
            b (-): Required argument on action functions for buttons.

        Returns:
            None

        """
        if hasattr(self, "nlq"):
            for d in self.proc_entities["CONDITION"]:
                if d["Text"] == self.mapped_condition_category.value:
                    d["Query-arg"] = self.mapped_update_condition_text.value
                    break

            self._visualize_condition_info()
            self._display_main()
        else:
            self._triger_no_input_warning()

    def visualize_entities(self, entities, converter):
        """Show the detected entities.

        Args:
            entities (dict): Detected entities in a NLQ.
            converter (function): Function reformatting the NLQ and entities for the detection visualizer

        Returns:
            IPython.core.display.HTML: HTML that will be passed for display and show the detected entities.

        """
        parsed = [converter(self.nlq, entities)]
        html = renderer.render(parsed, page=False, minify=False).strip()
        return HTML('<span class="tex2jax_ignore">{}</span>'.format(html))

    def _display_main(self, results=None, sql_query=None, rendered_sql=None):
        """Display the main output

        Args:
            results (pd.DataFrame): Results from the execute query. Default None for not printing.
            sql_query (str): Predicted general SQL query. Default None for not printing.
            rendered_sql (str): Rendered SQL query. Default None for not printing.

        Returns:
            None

        """
        self.general_output_vsection.clear_output()
        html_detected_entities = self.visualize_entities(
            self.entities, prepare_visualization_input_for_raw_entities
        )
        html_replaced_entities = self.visualize_entities(
            self.proc_entities, prepare_visualization_input_for_processed_entities
        )

        with self.general_output_vsection:
            print("\n• The following key entities have been detected:")
            display(html_detected_entities)
            print(
                "\n• Drugs and Conditions will be respectively replaced by the following RxNorm & ICD10 codes:"
            )
            display(html_replaced_entities)

            if sql_query:
                print("\n• Predicted SQL query:")
                display(sql_query)
            if rendered_sql:
                print("\n• Rendered SQL query:")
                display(rendered_sql)
            if isinstance(results, pd.DataFrame):
                print("\n• Request run successfully ✅. Results in the following table:")
                display(results)
            elif isinstance(results, str):
                print(results)

    def _update_options(self):
        """Update options of available drugs and conditions in the disambiguation tab.

        Args:
            None

        Returns:
            None

        """
        self.mapped_drug_category.options = [d["Text"] for d in self.entities["DRUG"]]
        self.mapped_condition_category.options = [
            d["Text"] for d in self.entities["CONDITION"]
        ]
        self.remove_name.options = [
            "{:s} (category: {:s})".format(d["Text"], cat_name)
            for cat_name, cat_dict in self.entities.items()
            for d in cat_dict
        ]

    def _display_name_info(self, text):
        """Dispaly `text` in the disambiguation info output.

        Args:
            text (str): Detected entities in a NLQ.

        Returns:
            None.

        """
        self.disambiguation_info_output.clear_output()
        with self.disambiguation_info_output:
            print(text)

    def _visualize_drug_info(self):
        """Dispaly drug information in the disambiguation output.

        Args:
            None

        Returns:
            None

        """

        # get dictionary of selected text
        entity_dict = [
            d
            for d in self.proc_entities["DRUG"]
            if d["Text"] == self.mapped_drug_category.value
        ][0]

        # output text
        lines = ["\t\t\t     TEXT: {}".format(entity_dict["Text"])]
        lines.append("\t\t\tDISAMBIGUATED TO: {}\n".format(entity_dict["Query-arg"]))
        lines.append("INFERRED OPTIONS")
        lines.append("    Score\tRxNorm Code   \tName\n")
        for i, d in enumerate(entity_dict["Options"], 1):
            lines.append(
                "{}. ({:.3f})\t {:7d} \t{}".format(
                    i, d["Score"], int(d["Code"]), d["Description"]
                )
            )
        text = "\n".join(lines)

        # display
        self._display_name_info(text)

    def _visualize_condition_info(self):
        """Dispaly condition information in the disambiguation output.

        Args:
            None

        Returns:
            None

        """
        # get dictionary of selected text
        entity_dict = [
            d
            for d in self.proc_entities["CONDITION"]
            if d["Text"] == self.mapped_condition_category.value
        ][0]

        # output text
        lines = ["\t\t\t     TEXT: {}".format(entity_dict["Text"])]
        lines.append("\t\t\tDISAMBIGUATED TO: {}\n".format(entity_dict["Query-arg"]))
        lines.append("INFERRED OPTIONS")
        lines.append("    Score\tICD10 Code   \tName\n")
        for i, d in enumerate(entity_dict["Options"], 1):
            lines.append(
                "{}. ({:.3f})\t {:7s} \t{}".format(
                    i, d["Score"], d["Code"], d["Description"]
                )
            )
        text = "\n".join(lines)

        # display
        self._display_name_info(text)

    def _triger_no_input_warning(self):
        """Display a warning message for missing nlq input.

        Args:
            None

        Returns:
            None

        """
        self.general_output_vsection.clear_output()
        with self.general_output_vsection:
            print(
                "\n⛔️ Please provide a valid query in 'Main' and click 'Detect' before using this functionality"
            )
