# pepper

Repository for Robot Applications created as part of the [Computational Lexicology & Terminology Lab (CLTL)](http://www.cltl.nl) at the Vrije Universiteit, Amsterdam.

**This is to run the leolani platform on your local x86 Ubuntu machine. It's not intended for the robot use. Everything is written in python3.**

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

* A x86 Ubuntu machine (Talk to the other authors for OSX)
* Python 3.7.9 environment
* Credentials for wolfram
* Credentials for google APIs
* [Docker Engine](https://docs.docker.com/engine/install/)

## How to start

I assume that you are doing everything in the directory where this `README.md` is located.

1. Start from a python3.7.9 environment (highly recommended)
2. Copy `credentials.config` and `google_cloud_key.json` into `config/` directory. Ask the authors if you have problems with this. `credentials.config` is for wolfram and `google_cloud_key.json` is for google APIs.
3. Install portaudio and java by running
    > `sudo apt-get install portaudio19-dev default-jdk` 
4. Install the required python modules by running 
    > `pip install -r requirements.txt`.
5. Clone the repo pepper_tensorflow by running 
    > `git clone https://github.com/leolani/pepper_tensorflow.git`
6. Build the pepper_tensorflow docker image 
    > `cd pepper_tensorflow && docker build -t cltl/pepper_tensorflow . && cd ..`
7. Download and install GraphDB version 9.3.1 binary by copying the below URL in your web browser
    > https://drive.google.com/file/d/1D0XzDSbdWc1FfQBVT_frHotH6d_haaYO/view?usp=sharing
8. Move the downloaded GraphDB zipfile `graphdb-free-9.3.1-dist.zip` into `setup/graphdb-docker/lib`.
9. Run the docker images by typing
    > `cd setup && docker-compose up && cd ..`
    
    This will start:
    * bamos/openface
    * GraphDB
    * pepper_tensorflow


    Data used by these containers is stored in `setup/data` and can be reset by removing all subfolders of that folder. Depending on your docker setup make sure the docker containers have enough memory and CPU available.

10. Make sure there is a GraphDB repository named `leolani`. If  not, run 
    
    > ` ./setup/setup-graphdb-repo.sh`.
    
    If this script fails, you may create the repository manually by accessing `http://localhost:7200/webapi` on your browser. Under `Repository Management`, use the `POST` endpoint to upload the `/setup/repo-config.ttl` file.

11. The directory `pepper` has to be in the PYTHONPATH. So everytime you run an example, be sure to write `PYTHONPATH="."` before starting an example file.

    For example,
    > `PYTHONPATH="." python apps/examples/greeting.py`   

12. Start other applications in `pepper/apps/`

    For example,
    > `PYTHONPATH="." python apps/hmk.py `   


13. Start/Stop Docker by running `cd setup && docker-compose start/stop && cd ..` when stopping/restarting the application.


## Usage

See [How to start](#how-to-start)

## Examples

See number 11 and number 12 in [How to start](#how-to-start)

## TODOs

1. Web GUI is not working. Some kind of threading error. Fix this.
2. Make Mac and Ubuntu have the same dependencies, or at least document them both thoroughly.
3. Better documentation
4. Clean code
5. Minimize the dependencies
6. Integrate [cltl-face-all](https://github.com/leolani/cltl-face-all)
7. Make docker easy.
8. Replace wolfram alpha, if possible
9. Run google APIs locally, if possible
10. Add tests
11. Package pepper into a python module so that it can run in any paths and environments.


## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Authors
* Selene Baez (s.baezsantamaria@vu.nl)
* Taewoon Kim (t.kim@vu.nl)
* Thomas Baier (t.baier@vu.nl)

## License
[MIT](https://choosealicense.com/licenses/mit/)