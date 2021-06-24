ML Model Development
====================

To train/fine-tune a pretrained T5 model (E.g., WikiSQL), you first need to update the model configuration file `t5_config.py`. Especially, you need to specify the input `data_dir` and `output_dir` for input data and model output directory respectively. The model training script is located in `t5_training.py`.

Once you train the model, you can also run the inference on the whole validation and test sets and compute the model performance (exact-matching and execution accuracies). The model evaluation script is located in `t5_evaluation.py`.

You can also test trained model and run inference for a single input question. The inference script is located in `t5_inference.py`. Update the necessary information and run the script to run the inference.

The end-to-end model development process is summarized in the diagram below.

.. figure:: _static/model_dev.png
   :scale: 100 %
   :align: center
   
   The ML Model Development Process.