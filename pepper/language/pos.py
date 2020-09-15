from nltk.tag.stanford import StanfordPOSTagger
from pepper import logger
import os

import pkgutil

data = pkgutil.get_data(__name__, "templates/temp_file")
class POS(object):
    """Part of Speech tagging using Stanford POSTagger"""

    package_root = os.path.dirname(__file__)
    STANFORD_POS = os.path.join(package_root, 'stanford-pos')
    STANFORD_POS_JAR = os.path.join(STANFORD_POS, 'stanford-postagger.jar')
    STANFORD_POS_TAGGER = os.path.join(STANFORD_POS, 'models/english-bidirectional-distsim.tagger')
    
    def __init__(self):
        self._log = logger.getChild(self.__class__.__name__)
        self._tagger = StanfordPOSTagger(POS.STANFORD_POS_TAGGER, path_to_jar=POS.STANFORD_POS_JAR)

    def tag(self, tokens):
        """
        Tag Part of Speech using Stanford NER

        Parameters
        ----------
        tokens

        Returns
        -------
        POS: list of tuples of strings
        """

        try:
            return self._tagger.tag(tokens)
        except Exception as e:
            self._log.error("Couldn't connect to Java POS Server. Do you have Java installed?")
            self._log.error(e)
            return [(token, 'ERROR') for token in tokens]
