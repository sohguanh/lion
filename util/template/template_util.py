import io
import os
import logging
from string import Template

import config

# key is filename, value is Template
registered_templates = {}


def register_template(config, dbPool):
    logging.info('register all templates ...')
    path = config['TemplateConfig']['Path']
    file_ext = config['TemplateConfig']['FileExt']
    if path is None or not (os.path.isdir(path) and os.path.exists(path)):
        return

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(file_ext):
                with io.open(os.path.join(root, name), mode="r", encoding="utf-8") as f:
                    registered_templates[name.split(file_ext)[0]] = Template(f.read())


def get_template(name) -> Template:
    return registered_templates[name] if name in registered_templates else None
