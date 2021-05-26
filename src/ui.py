import ipywidgets as widgets
from ipywidgets import Layout, Text, Textarea, Dropdown, Combobox, Button, Output, HBox, VBox, Tab, Password, RadioButtons
import re
from spacy import displacy
import config
from IPython.core.display import display, HTML
from copy import deepcopy
import time
import pandas as pd
from pprint import pprint
import os
from os import path as osp
import json
import datetime

MAIN_BOX_LAYOUT = Layout(flex='1 1 auto', height='1200px', min_height='50px', width='auto')
MAIN_CREDENTIALS_LAYOUT = Layout(height='5%', width='90%')
MAIN_INTERFACE_LAYOUT = Layout(height='30%', width='90%')# flex='0 1 auto',
MAIN_DISPLAY_LAYOUT = Layout(flex='0 1 auto', height='50%', width='90%', border='1px solid black')
MAIN_FEEDBACK_LAYOUT = Layout(flex='0 1 auto', height='5%', width='90%')#, border='1px solid black')

INPUT_BOX_LAYOUT = Layout(flex='1 1 auto', height='100%', min_height='50px', width='auto')
INPUT_TEXT_LAYOUT = Layout(height='90%', width='90%')# flex='0 1 auto',
# INPUT_DISPLAY_LAYOUT = Layout(flex='0 1 auto', height='70%', width='90%', border='1px solid black')

SUB_DETECT_BOX_LAYOUT = Layout(flex='1 1 auto', height='40%', min_height='50px', width='auto')
DETECT_BOX_LAYOUT = Layout(flex='1 1 auto', height='auto', min_height='50px', width='auto')
INFO_BOX_LAYOUT =  Layout(flex='1 1 auto', height='100%', min_height='50px', width='auto')
# INPUT_TEXT_LAYOUT = Layout(flex='0 1 auto', height='95%', width='90%')

RENDERER = displacy.EntityRenderer(options={})

RENDERER.colors = {
    'DRUG': '#7aecec',
    'CONDITION': '#bfeeb7',
    'AGE': '#feca74',
    'STATE': '#ff9561',
    'ETHNICITY': '#aa9cfc',
    'RACE': '#c887fb',
    'TIMEDAYS': '#bfe1d9',
    'TIMEYEARS': '#bfe1d9',
    'GENDER': '#e4e7d2',
#     'FACILITY': '#9cc9cc',
#     'EVENT': '#ffeb80',
#     'LAW': '#ff8197',
#     'LANGUAGE': '#ff8197',
#     'WORK_OF_ART': '#f0d0ff'
}

# create logs folder if it does not exist
if not osp.exists('.logs'):
    os.makedirs('.logs')
    
# today_fn = datetime.date.today().strftime("%Y_%m_%d") + '.txt'
# today_fp = osp.join('.logs', today_fn)

def reformat_raw_entities(entities):
    out = [{
        'start': name_dict['BeginOffset'],
        'end': name_dict['EndOffset'],
        'label': category
           } 
           for category, name_dicts in entities.items() 
           for name_dict in name_dicts
          ]
    out = sorted(out, key=lambda x: x['start'])
    return out

def raw_converter(text, entities):
    ents = reformat_raw_entities(entities)
    out = {
        'text': text,
        'ents': ents,
        'title': None,
        'settings': {'lang': 'en', 'direction': 'ltr'}
    }
    return out


def get_reformatted_proc_entities(text, entities):
    out = []
    for category, name_dicts in entities.items():
        for name_dict in name_dicts:
            repl_text = name_dict['Query-arg']
            p = re.compile(f"(?i)\\b{repl_text}\\b")
            match = list(re.finditer(p, text))[0]
            out.append({
                'start': match.start(),
                'end': match.end(),
                'label': category
            })
    out = sorted(out, key=lambda x: x['start'])
    return out


def get_reformatted_nlq(text, entities):
    out_text = deepcopy(text)
    for cat_entities in entities.values():
        for entity in cat_entities:
            orig_text = entity['Text']
            p = re.compile(f"(?i)\\b{orig_text}\\b")
            repl_text = entity['Query-arg']
            out_text = re.sub(p, repl_text, out_text)
    return out_text


def proc_converter(text, entities):
    text2 = get_reformatted_nlq(text, entities)
    ents = get_reformatted_proc_entities(text2, entities)
    out = {
        'text': text2,
        'ents': ents,
        'title': None,
        'settings': {'lang': 'en', 'direction': 'ltr'}
    }
    return out



class UI(object):
    
    def __init__(self, tool):
        
        self.tool = tool
        
        # initialize widgets
        self._initialize_credentials_box()
        self._initialize_inputs()
        self._initialize_add_detection()
        self._initialize_mapped_values()
        self._initialize_feedback_box()
        
        self._structure_main_layout()
        
    def _structure_main_layout(self):
        
        children = [self.input_disp_box, self.detection_box, self.disambiguate_box]
        self.tab = Tab(layout=MAIN_INTERFACE_LAYOUT)
        self.tab.children = children
        self.tab.set_title(0, 'Main')
        self.tab.set_title(1, 'Correct detection')
        self.tab.set_title(2, 'Correct code map')
        
        
        self.main_display = Output(layout=MAIN_DISPLAY_LAYOUT)
        
        
        self.main_ui = VBox([self.credentials_box, self.tab, self.main_display, self.feedback_box], layout = MAIN_BOX_LAYOUT)
        
        
    def _initialize_credentials_box(self):
        
        self.widget_db_user = Text(description='User:', layout={'width': '30%'})
        self.widget_db_password = Password(description='Password:', layout={'width': '30%'})
        self.white_space1 = Output(layout={'width': '25%'})
        self.set_credentials_button = Button(description="Set Data Credentials")
        self.set_credentials_button.on_click(self._record_db_credentials)
        
        self.credentials_box = HBox([self.widget_db_user, self.widget_db_password, self.white_space1, self.set_credentials_button], layout=MAIN_CREDENTIALS_LAYOUT)
        
        
    def _clear_output(self, b):
        self.main_display.clear_output()
        self.mapped_out.clear_output()
    
    
    def _log_feedback(self, b):
        
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        record = {
            'time': now,
            'input': self.nlq,
            'args original': self.original_proc_entities, # make a copy on "detect"
            'args corrected': self.proc_entities, # last version of args
            'correct': True if self.feedback_options.value=='Successful' else False
        }
        
        file_path = osp.join('.logs', now+'.txt')
        with open(file_path, 'a') as fp:
            json.dump(record, fp)
            
            
    def _clear_credentials(self, b):
        self.tool.clear_credentials()
    
    
    def _initialize_feedback_box(self):
        
        self.clear_output_button = Button(description="Clear Output")
        self.clear_output_button.on_click(self._clear_output)
        
        self.clear_credentials_button = Button(description="Forget Credentials")
        self.clear_credentials_button.on_click(self._clear_credentials)
        
        self.processing_flag = Output(layout={'width': '30%'})
        
        self.feedback_options = RadioButtons(
            value='Successful',
            options=['Successful', 'Unsuccessful'],
            description='Feedback:',
            layout={'width': '25%'}
        )
        
        self.submit_button = Button(description="Submit feedback")
        self.submit_button.on_click(self._log_feedback)
        
        
        self.feedback_box = HBox([self.clear_output_button, self.clear_credentials_button,  self.processing_flag, self.feedback_options, self.submit_button], layout=MAIN_FEEDBACK_LAYOUT)
        
        
    def _record_db_credentials(self, b):
        
        db_user = self.widget_db_user.value
        db_password = self.widget_db_password.value
        self.tool.set_db_credentials(db_user, db_password)
    
    
    def visualize_entities(self, entities, converter):
        parsed = [converter(self.nlq, entities)]
        html = RENDERER.render(parsed, page=False, minify=False).strip()
        return HTML('<span class="tex2jax_ignore">{}</span>'.format(html))


    def _display_main(self, results=None):
        self.main_display.clear_output()
        html_detected_entities = self.visualize_entities(self.entities, raw_converter)
        html_replaced_entities = self.visualize_entities(self.proc_entities, proc_converter)
        
        with self.main_display:
            print("\n• The following key entities have been detected:")
            display(html_detected_entities)
            print("\n• Drugs and Conditions will be respectively replaced by the following RxNorm & ICD10 codes:")
            display(html_replaced_entities)
            if isinstance(results, pd.DataFrame):
                print("\n• Request run successfully ✅. Results in the following table:")
                display(results)
            elif isinstance(results, str):
                print(results)
    
    
    def _helper_detect_button(self, b):
        self.nlq = self.input_box.value
        self.entities = self.tool.detect_entities(self.nlq)
        self.proc_entities = self.tool.process_entities(self.entities)
        self.original_proc_entities = deepcopy(self.proc_entities)
        
        self._display_main()
        self._update_options()
        
        
    def _helper_execute_button(self, b):
        if self.tool.credentials_exist():
        
            with self.processing_flag:
                print("🕝 Processing ....")

            nlq_w_placeholders = self.tool.replace_name_for_placeholder(self.nlq, self.proc_entities)
            sql_query = self.tool.ml_call(nlq_w_placeholders)


            try:
                rendered_sql_query = self.tool.render_template_query(sql_query, self.proc_entities)
                output = self.tool.execute_sql_query(rendered_sql_query)
            except:
                output = '\n•An error ocurred. We apologise for the inconvenience. Please try to re-formulate your query.'
        
        else:
            output = "\n⛔️ Please set your data credentials to execute the query."
        
        self._display_main(output)
        
        self.processing_flag.clear_output()
            
    
    def _initialize_inputs(self):
        
        self.input_box = Textarea(
            placeholder='e.g. Number of patients taking Aspirin',
            description='Query:',
            layout=INPUT_TEXT_LAYOUT,
            disabled=False
        )
        self.detect_button = Button(description="Detect")
        self.detect_button.on_click(self._helper_detect_button)
        self.execute_button = Button(description="Execute")
        self.execute_button.on_click(self._helper_execute_button)
        
        self.main_buttons = HBox([self.detect_button, self.execute_button])
        self.input_disp_box = VBox([self.input_box, self.main_buttons], layout=INPUT_BOX_LAYOUT)
        
    
    def _update_options(self):
        self.mapped_drug_category.options = [d['Text'] for d in self.entities['DRUG']]
        self.mapped_condition_category.options = [d['Text'] for d in self.entities['CONDITION']]
        self.remove_name.options = ["{:s} (category: {:s})".format(d['Text'], cat_name) for cat_name, cat_dict in self.entities.items() for d in cat_dict]
        
    
    def _record_name(self, b):
        name = self.add_name.value
        category = self.add_category.value
        
        p = re.compile(f"(?i)\\b{name}\\b")
        # current entities set
        current_names = set([d['Text'] for d in self.entities[category]])
        if name not in current_names:
            for match in re.finditer(p, self.nlq):
                detected_entity = {
                        'BeginOffset': match.start(),
                        'EndOffset': match.end(),
                        'Text': name
                }
                
                # add to raw entities
                self.entities[category].append(
                    deepcopy(detected_entity)
                )
                
                # process & add to proc entities
                placeholder_idx_strat = {
                    category: len(self.proc_entities[category])
                }
                proc_detected_entity = self.tool.process_entities(
                    {category: [deepcopy(detected_entity)]}, 
                    start_indices=placeholder_idx_strat
                )
                self.proc_entities[category].append(
                    proc_detected_entity[category][0]
                )   
        self._display_main()
        self._update_options()
        
    def _remove_name(self, b):
        # do removing
        remove_name_category = self.remove_name.value
        name, category = remove_name_category.split(' (category: ')
        category = category[:-1]
        
        # remove from entities
        for i in range(len(self.entities[category])):
            if self.entities[category][i]['Text']==name:
                del self.entities[category][i]
                break
        
        # remove from proc_entities
        for i in range(len(self.proc_entities[category])):
            if self.proc_entities[category][i]['Text']==name:
                del self.proc_entities[category][i]
                break
                
        self._display_main()
        self._update_options()
        
    
    def _initialize_add_detection(self):
        
        self.add_sub_title_1 = Output()
        self.add_sub_title_1.append_stdout("Add detection")
        
        self.add_name = Text(
            placeholder='Aspirin 30Mg',
            description='Write name',
#             layout=TEXT_LAYOUT,
            disabled=False
        )
        self.add_category = Dropdown(
            # value='John',
            placeholder='Choose entity',
            options=['DRUG', 'CONDITION', 'AGE', 'STATE', 'ETHNICITY', 'RACE', 'TIMEDAYS', 'TIMEYEARS', 'GENDER'],
            description='Category:',
            ensure_option=True,
            disabled=False
        )
        self.add_button = Button(description="Highlight")
        self.add_button.on_click(self._record_name)
        
        self.add_box = HBox([self.add_name, self.add_category, self.add_button], layout=SUB_DETECT_BOX_LAYOUT)
        
        self.remove_sub_title_2 = Output()
        self.remove_sub_title_2.append_stdout("Remove detection")
        
        self.remove_name = Dropdown(
            # value='John',
            placeholder='',
            options=[],
            description='Name:',
            ensure_option=True,
            disabled=False
        )
        self.remove_button = Button(description="Remove")
        self.remove_button.on_click(self._remove_name)
        
        self.remove_box = HBox([self.remove_name, self.remove_button], layout=SUB_DETECT_BOX_LAYOUT)
        
        self.detection_box = VBox([self.add_sub_title_1, self.add_box, self.remove_sub_title_2, self.remove_box], 
                                  layout=DETECT_BOX_LAYOUT)
           
    
    def _display_name_info(self, text):
        self.mapped_out.clear_output()
        with self.mapped_out:
            print(text)
    
    
    
    def _visualize_drug_info(self,):
    
        # get dictionary of selected text
        entity_dict = [d for d in self.proc_entities['DRUG'] if d['Text'] == self.mapped_drug_category.value][0]
        
        # output text
        lines = ["\t\t\t     TEXT: {}".format(entity_dict['Text'])]
        lines.append("\t\t\tDISAMBIGUATED TO: {}\n".format(entity_dict['Query-arg']))
        lines.append("INFERRED OPTIONS")
        lines.append("    Score\tRxNorm Code   \tName\n")
        for i, d in enumerate(entity_dict['Options'], 1):
            lines.append("{}. ({:.3f})\t {:7d} \t{}".format(i, d['Score'], int(d['Code']), d['Description']))
        text = '\n'.join(lines)
        
        # display
        self._display_name_info(text)
#         self.mapped_out.clear_output()
#         self.mapped_out.append_stdout(text)
        
        
    def _visualize_condition_info(self,):
        # get dictionary of selected text
        entity_dict = [d for d in self.proc_entities['CONDITION'] if d['Text'] == self.mapped_condition_category.value][0]
        
        # output text
        lines = ["\t\t\t     TEXT: {}".format(entity_dict['Text'])]
        lines.append("\t\t\tDISAMBIGUATED TO: {}\n".format(entity_dict['Query-arg']))
        lines.append("INFERRED OPTIONS")
        lines.append("    Score\tICD10 Code   \tName\n")
        for i, d in enumerate(entity_dict['Options'], 1):
            lines.append("{}. ({:.3f})\t {:7s} \t{}".format(i, d['Score'], d['Code'], d['Description']))
        text = '\n'.join(lines)
        
        # display
        self._display_name_info(text)
        
    def _triger_no_input_warning(self):
        self.main_display.clear_output()
        with self.main_display:
            print("\n⛔️ Please provide a valid query in 'Main' and click 'Detect' before using this functionality")
    
    
    def _drug_info(self, b):
        if hasattr(self, 'nlq'):
            self._visualize_drug_info()
        else:
            self._triger_no_input_warning()
        
    
    def _condition_info(self, b):
        if hasattr(self, 'nlq'):
            self._visualize_condition_info()
        else:
            self._triger_no_input_warning()
        
    
    def _drug_update(self, b):
        if hasattr(self, 'nlq'):
            for d in self.proc_entities['DRUG']:
                if d['Text'] == self.mapped_drug_category.value:
                    d['Query-arg'] = self.mapped_update_drug_text.value
                    break

            self._visualize_drug_info()
            self._display_main()
        else:
            self._triger_no_input_warning()
        
    def _condition_update(self, b):
        if hasattr(self, 'nlq'):
            for d in self.proc_entities['CONDITION']:
                if d['Text'] == self.mapped_condition_category.value:
                    d['Query-arg'] = self.mapped_update_condition_text.value
                    break

            self._visualize_condition_info()
            self._display_main()
        else:
            self._triger_no_input_warning()
    
    
    def _initialize_mapped_values(self,):
        
#         DRUG
        drugs = [d['Text'] for d in self.entities['DRUG']] if hasattr(self, 'entities') else []
        self.mapped_drug_category = Dropdown(
            placeholder='e.g. Aspirin',
            options=drugs,
            description='Drug',
            ensure_option=True,
            disabled=False
        )
        self.mapped_drug_button = Button(description="Show drug info")
        self.mapped_drug_button.on_click(self._drug_info)
        self.mapped_update_drug_text = Text(
            placeholder='RxNorm code',
            description='Map to',
#             layout=TEXT_LAYOUT,
            disabled=False
        )
        self.mapped_update_drug_button = Button(description="Update drug")
        self.mapped_update_drug_button.on_click(self._drug_update)
        
#         CONDITION
        conditions = [d['Text'] for d in self.entities['CONDITION']] if hasattr(self, 'entities') else []
        self.mapped_condition_category = Dropdown(
            placeholder='e.g. Insomnia',
            options=conditions,
            description='Condition',
            ensure_option=True,
            disabled=False
        )
        self.mapped_condition_button = Button(description="Show condition info")
        self.mapped_condition_button.on_click(self._condition_info)
        self.mapped_update_condition_text = Text(
            placeholder='ICD10 code',
            description='Map to',
#             layout=TEXT_LAYOUT,
            disabled=False
        )
        self.mapped_update_condition_button = Button(description="Update condition")
        self.mapped_update_condition_button.on_click(self._condition_update)
        
        
        self.mapped_out = Output(layout={'border': '1px solid black'})
        
        self._mapped_drug_box = HBox([self.mapped_drug_category, self.mapped_drug_button, self.mapped_update_drug_text, self.mapped_update_drug_button])
        self._mapped_condition_box = HBox([self.mapped_condition_category, self.mapped_condition_button, self.mapped_update_condition_text, self.mapped_update_condition_button])
        
        self.disambiguate_box = VBox([self._mapped_drug_box, self._mapped_condition_box, self.mapped_out], layout=INFO_BOX_LAYOUT)
        
        
    def main(self):
        display(self.main_ui)
        
        
