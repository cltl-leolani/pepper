"""
The Pepper Configuration File contains Settings for:

- Application Backend, Language, Paths & URLs
- API Keys (Google Cloud Services & Wolfram Alpha)
- Sensory Parameters (tweak for desired performance)

(see source file for more information)

"""

import pepper
import json
import os

# <<< Application Configuration Settings >>>

# Application Backend to Use (SYSTEM or NAOQI)
APPLICATION_BACKEND = pepper.ApplicationBackend.NAOQI

# Name of Unknown and Groups of Humans
HUMAN_UNKNOWN = "Stranger"
HUMAN_CROWD = "Humans"

# <<< Application Paths >>>

# pepper/                  PROJECT_ROOT
#   people/                 PEOPLE_ROOT
#       friends/             PEOPLE_FRIENDS_ROOT
#           friend001.bin     files containing OpenFace feature data (nx128, for any n > 0)
#           friend002.bin     the name of each file represents the name of a friend
#           friend003.bin     drag 'n drop people from people/new/ to people/friends to update their status
#           ...
#       new/                 PEOPLE_NEW_ROOT
#           NEW.bin           special file containing OpenFace feature data for all faces in LFW dataset
#           new_person1.bin   files containing OpenFace feature data for each new person met
#           ...
#   pepper/                 PACKAGE_ROOT
#       apps/                application implementations
#       brain/               brain (triple store) interactions
#       framework/           application building blocks
#       knowledge/           knowledge sources
#       language/            natural language processing
#       sensor/              sensory processing
#       ...
#       config.py            << this file >>
#       log.txt              LOG
#       brain_log.trig       BRAIN_LOG_ROOT
#       ...
#   README.md               ReadMe File
#   google_cloud_key.json   Google Cloud Key
#

# Path to Package Root (see tree above)
PACKAGE_ROOT = os.path.dirname(__file__)

# Path to Project Root (see tree above)
PROJECT_ROOT = os.path.join(*os.path.split(PACKAGE_ROOT)[:-1])

# People Root
PEOPLE_ROOT = os.path.join(os.path.dirname(__file__), '../people')

# Root of Robot's "friends"
PEOPLE_FRIENDS_ROOT = os.path.join(PEOPLE_ROOT, 'friends')

# Root of people Robot has "just met"
PEOPLE_NEW_ROOT = os.path.join(PEOPLE_ROOT, 'new')

# Names of Friends
PEOPLE_FRIENDS_NAMES = [os.path.splitext(path)[0] for path in os.listdir(PEOPLE_FRIENDS_ROOT) if path.endswith(".bin")]

# Path to GOOGLE_APPLICATION_CREDENTIALS file (.json)
# See for more details: https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries
KEY_GOOGLE_CLOUD = os.path.join(os.path.dirname(__file__), "../google_cloud_key.json")

if not os.path.exists(KEY_GOOGLE_CLOUD):
    print("WARNING: {} does not exist, \n"
          "         Google Cloud Services will not work.\n"
          "         See https://github.com/cltl/pepper/wiki/Installation#2-google-cloud-services"
          "for more information\n".format(KEY_GOOGLE_CLOUD))

# Path to other tokens (currently just WolframAlpha)
# See for more details: https://products.wolframalpha.com/spoken-results-api/documentation/
# Please make sure you create this .json file with the following formatting:
# {
#  "wolfram": "<Your Wolfram Alpha Key>"
# }
KEY_WOLFRAM = os.path.join(os.path.dirname(__file__), '../tokens.json')

if not os.path.exists(KEY_WOLFRAM):
    print("WARNING: {} does not exist, \n"
          "         Wolfram Alpha will not work.\n"
          "         See https://github.com/cltl/pepper/wiki/Installation#7-wolfram-alpha"
          "for more information\n".format(KEY_WOLFRAM))

# General Logging
LOG = pepper.LOGGING_FILE

# Brain Logging
BRAIN_LOG_ROOT = os.path.join(PACKAGE_ROOT, "../backups/brain/brain_log_{}")

# <<< Application URLs >>>

# Brain URL (Local GraphDB or Remote Database)
BRAIN_URL_LOCAL = "http://localhost:7200/repositories/leolani"
BRAIN_URL_REMOTE = "http://145.100.58.167:50053/sparql"

# .json file with id tokens, with keys:
#   "wolfram": <appid>
with open(KEY_WOLFRAM) as tokens:
    TOKENS = json.load(tokens)

# Set GOOGLE CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_GOOGLE_CLOUD
