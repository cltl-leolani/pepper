import os
import re
import string
from datetime import date

import numpy as np

from pepper.api import Emotion
from pepper.brain.utils.constants import CAPITALIZED_TYPES


def read_query(query_filename):
    """
    Read a query from file and return as a string
    Parameters
    ----------
    query_filename: str name of the query. It will be looked for in the queries folder of this project

    Returns
    -------
    query: str the query with placeholders for the query parameters, as a string to be formatted

    """
    with open(os.path.join(os.path.dirname(__file__), "../queries/{}.rq".format(query_filename))) as fr:
        query = fr.read()
    return query


def is_proper_noun(types):
    return any(i in types for i in CAPITALIZED_TYPES)


def casefold_text(text, format='triple'):
    if format == 'triple':
        if isinstance(text, str):
            for sign in string.punctuation:
                text = text.replace(sign, "-")

            text = text.lower().replace(" ", "-").strip('-')

        return re.sub('-+', '-', text)

    elif format == 'natural':
        return text.lower().replace("-", " ").strip() if isinstance(text, str) else text

    else:
        return text


def casefold_capsule(capsule, format='triple'):
    """
    Function for formatting a capsule into triple format or natural language format
    Parameters
    ----------
    capsule:
    format

    Returns
    -------

    """
    for k, v in list(capsule.items()):
        if isinstance(v, dict):
            capsule[k] = casefold_capsule(v, format=format)
        else:
            capsule[k] = casefold_text(v, format=format)

    return capsule


def date_from_uri(uri):
    [year, month, day] = uri.split('/')[-1].split('-')
    return date(int(year), int(month), int(day))


def hash_claim_id(triple):
    return '_'.join(triple)


def confidence_to_certainty_value(confidence):
    if confidence is not None:
        confidence = float(confidence)
        if confidence > .90:
            return 'CERTAIN'
        elif confidence >= .50:
            return 'PROBABLE'
        elif confidence > 0:
            return 'POSSIBLE'
    return 'UNDERSPECIFIED'


def polarity_to_polarity_value(polarity):
    if polarity is not None:
        polarity = float(polarity)
        if polarity > 0:
            return 'POSITIVE'
        elif polarity < 0:
            return 'NEGATIVE'
    return 'UNDERSPECIFIED'


def sentiment_to_sentiment_value(sentiment):
    if sentiment is not None:
        sentiment = float(sentiment)
        if sentiment > 0:
            return 'POSITIVE'
        elif sentiment < 0:
            return 'NEGATIVE'
        elif sentiment == 0:
            return 'NEUTRAL'
    return 'UNDERSPECIFIED'


def emotion_to_emotion_value(emotion):
    if emotion is not None:
        if emotion == Emotion.ANGER:
            return 'ANGER'
        elif emotion == Emotion.DISGUST:
            return 'DISGUST'
        elif emotion == Emotion.FEAR:
            return 'FEAR'
        elif emotion == Emotion.JOY:
            return 'JOY'
        elif emotion == Emotion.SADNESS:
            return 'SADNESS'
        elif emotion == Emotion.SURPRISE:
            return 'SURPRISE'
        elif emotion == Emotion.NEUTRAL:
            return 'NEUTRAL'
    return 'UNDERSPECIFIED'


def replace_in_file(file, word, word_replacement):
    for i, line in enumerate(open(file)):
        line.replace(':%s' % word, ':%s' % word_replacement)
        line.replace('"%s' % word, '"%s' % word_replacement)


def get_object_id(memory, category):
    cat_mem = memory.get(casefold_text(category, format='triple'), {'brain_ids': [], 'local_ids': [], 'ids': []})
    l = cat_mem['ids'][:]
    id = l[0]
    tail = l[1:]

    cat_mem['ids'] = tail
    memory[casefold_text(category, format='triple')] = cat_mem
    return id, memory


def sigmoid(z, growth_rate=1):
    return 1 / (1 + np.exp(-z * growth_rate))
