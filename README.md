# VU Amsterdam - CLTL - Robot Framework

Repository for Robot Applications created as part of the [Computational Lexicology & Terminology Lab (CLTL)](http://www.cltl.nl) at the Vrije Universiteit, Amsterdam.

| **This is a Python 3 version of the Leolani platform and is not intended for the robot use. It does not support the NAOqi backend! Currently it's only tested on Linux and Mac.** |
|---|

![Pepper Robot Leolani](images/pepper.png)

## Features
 - A framework for creating interactive Robot Applications using Python, to enable:
   - Human-Robot conversation using Speech-to-Text and Text-to-Speech
   - Recognising friends by face and learning about them and the world through conversation
   - Recognising and positioning the people and objects in its enviroment.
 - Natural Language Understanding through Syntax Trees (Grammars)
 - Knowledge Representation of all learned facts through a RDF Graph: Pepper's Brain!
 - Curiosity based on Knowledge Gaps and Conflicts resulting from learned facts
 - Realtime visualisation in web browser

## Getting started
Check out our [WIKI](https://github.com/cltl/pepper/wiki) for information on [how it works](https://github.com/cltl/pepper/wiki/2.-Code-Structure).

Check out our [API Reference](https://cltl.github.io/pepper/) and [Sample Applications](https://github.com/cltl/pepper/tree/develop/apps/examples)!

| **Part of the WIKI still references the Python 2.7 version of Leolani!** |
|---|


## More information
More information on the Pepper project at CLTL can be found on http://makerobotstalk.nl

## Features
 - A framework for creating interactive Robot Applications using Python, to enable:
   - Human-Robot conversation using Speech-to-Text and Text-to-Speech
   - Recognising friends by face and learning about them and the world through conversation
   - Recognising and positioning the people and objects in its enviroment.
 - Natural Language Understanding through Syntax Trees (Grammars)
 - Knowledge Representation of all learned facts through a RDF Graph: Pepper's Brain!
 - Curiosity based on Knowledge Gaps and Conflicts resulting from learned facts
 - Realtime visualisation in web browser

## Prerequisites

* Python 3.7.9 environment
* An application on [Wolfram Alpha](https://products.wolframalpha.com/api/) with for API access
* A project on the Google Cloud Platform supporting Text-To-Speech and Speech-To-Text APIs
* [Docker Engine](https://docs.docker.com/engine/install/)

## How to start

We assume that the following steps are executed in in the directory where this `README.md` is located.

1. Clone this repo by running
    > `git clone https://github.com/leolani/pepper.git`

1. Checkout to this branch by running
    > `git checkout feature/python3.7`

1. Start from a python 3.7.9 environment (highly recommended).
    To create an isolated environment for the project run
    > `python -m venv venv` <br/> `source venv/bin/activate`

    To deactivate the environment after use type
    > `deactivate`    

1. Create a JSON key file for the service account used in your Google Cloud project and copy it to
`config/google_cloud_key.json`.
1. Setup an application at [WolframAlpha](https://products.wolframalpha.com/api/) and create a text file named
`config/credentials.config` with content:
    ```
   [credentials]
   wolfram: MY-APPLICATION-ID
   ```
1. Install Java, and on Linux install portaudio by running
    > `sudo apt-get install portaudio19-dev default-jdk` 
1. Install the required python modules by running 
    > `pip install -r linux_requirements.txt`

    on Linux or
    > `pip install -r mac_requirements.txt`

    on OS X or
    > `pip install -r windows_requirements.txt`

    on Windows

1. Clone the repo pepper_tensorflow into a separate workspace by running 
    > `cd .. && git clone https://github.com/leolani/pepper_tensorflow.git`

    Keep in mind that this changes your current directory.
1. Build the pepper_tensorflow docker image 
    > `cd pepper_tensorflow && docker build -t cltl/pepper_tensorflow .`

1. **Return to the root directory of this repository** and download [GraphDB](https://www.ontotext.com/products/graphdb/graphdb-free/)
    (You have to register your email and the link will be sent to your mailbox. Check the spam folder as well. Download the *standalone server* version). Move the zipfile to the `setup/graphdb-docker/lib` folder. In the `setup/docker-compose.yml`
    file adjust the GraphDB version to the version you just downloaded.

    If you use a local installation of GraphDB remove the GraphDB entry from `setup/docker-compose.yml` before starting
    the Docker images in the next step.
1. Run the Docker images needed by Leolani by typing
    > `cd setup && docker-compose up && cd ..`
    
    This will start:
    * bamos/openface
    * GraphDB
    * pepper_tensorflow

    Data used by these containers is stored in `setup/data` and can be reset by removing all subfolders of that directory.
    Depending on your Docker setup make sure the Docker containers have enough memory and CPU available.

1. Make sure there is a GraphDB repository named `leolani`. If  not, run 
    
    > ` ./setup/setup-graphdb-repo.sh`.
    
    If this script fails, you may create the repository manually by accessing `http://localhost:7200/webapi` on your browser.
    Under `Repository Management`, use the `POST` endpoint to upload the `/setup/repo-config.ttl` file.

1. The directory `pepper` has to be in the PYTHONPATH. So everytime you run an example, be sure to write `PYTHONPATH="."`
    before starting an example file.

    For example,
    
    > `PYTHONPATH="." python apps/examples/greeting.py`

    If you use an IDE to run the applications make sure that the workspace root is added to the python path, that
    the working directory for execution is the workspace root and not the directory containing the application script
    and, if a virtual environment was setup in step 1, it is used.   

1. Configurations for the application are set in `config/default.config` and individual items can be overriden in
`config/pepper.config`. Choose the backend right backend in `config/pepper.config` (only *system* is supported for the Python 3 version).
1. Start other applications in `pepper/apps/`

    For example,
    > `PYTHONPATH="." python apps/hmk.py `   


1. Start/Stop Docker by running `cd setup && docker-compose start/stop && cd ..` when stopping/restarting the application.

## Usage

See [How to start](#how-to-start)

## Examples

See number 11 and number 13 in [How to start](#how-to-start)

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
[MIT](https://choosealicense.com/licenses/mit/)