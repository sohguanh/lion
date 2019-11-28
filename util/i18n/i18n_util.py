import io
import os
import logging


class Locale:
    def __init__(self, language="en", country="US"):
        '''
        Country codes refer to Alpha-2 code from https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
        Language refer to ISO 639-1 Code from https://www.loc.gov/standards/iso639-2/php/code_list.php
        '''
        self.language = language
        self.country = country

    def get_language(self):
        return self.language

    def get_country(self):
        return self.country


class ResourceBundle:
    # key is bundle_language_country, value is dict of properties key
    # e.g __bundles['messages_en_US']['prop_key'], __bundles['messages_zh_CN']['prop_key'], __bundles['messages_zh_TW']['prop_key'] etc
    __bundles = {}

    @classmethod
    def get_bundle(cls, config, bundle: str, locale: Locale) -> dict:
        """ Static access method. """
        key = "".join([bundle, '_', locale.get_language(), '_', locale.get_country()])
        if key not in ResourceBundle.__bundles:
            ResourceBundle.__init_resource_bundle(config, key)
        return ResourceBundle.__bundles[key]

    @classmethod
    def __init_resource_bundle(cls, config, key):
        logging.debug("__init_resource_bundle: "+key)
        if config['i18nConfig']['Enable']:
            name = "".join([key, config['i18nConfig']['FileExt']])
            try:
                with io.open(os.path.join(os.getcwd(), config['i18nConfig']['Path'], name), mode="r", encoding="utf-8") as f:
                    props = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key_value = line.split('=')
                            prop_key = key_value[0].strip()
                            prop_value = '='.join(key_value[1:]).strip().strip('"')
                            props[prop_key] = prop_value
                    ResourceBundle.__bundles[key] = props
            except Exception as e:
                logging.error(e)
