LUMPSModel
==============================

Surface energy balance model implementation for a class.

The guiding principle for the code was making it so that each experiment could be described in a config file and live there to be self-documenting and reproducible:

/src/model/experiments/config/config.yaml 

If trying to understand the LUMPS code, good luck, but start at

/src/model/lumps.py

/notebooks has a single Jupyter notebook for just the radiation model portion of the code. It hasn't been updated to work with the current version of the code.

------------------------------
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
