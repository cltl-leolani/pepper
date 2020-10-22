Setup
-----

### Run the application

#### Run on Laptop
1. Set ```backend``` to ```system``` in the ```[DEFAULT]``` section of ```config/pepper.config```

#### Run on Robot
1. Set ```backend``` to ```naoqi``` in the ```[DEFAULT]``` section of ```config/pepper.py```
2. Set ```ip``` and ```port``` in accordance with robot's address in the ```[pepper.framework.backend.naoqi]``` of ```config/pepper.config```

#### Common steps to run the application

1. Build the Docker image for [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow)
  by running

    ```> docker build -t cltl/pepper_tensorflow .```
  in that repository.
2. Download GraphDB binary (`graphdb-free-<version>-dist.zip`) into `setup/graphdb-docker/lib`
3. Run `> docker-compose up` from the `setup/` folder. This starts
    * bamos/openface
    * GraphDB
    * pepper_tensorflow
   
   Data used by these containers is stored in `setup/data` and can be reset by removing all subfolders of that folder.
4. Make sure there is a GraphDB repository named `leolani`. If  not, run `> ./setup/setup-graphdb-repo.sh`. 
   If this script fails, you may create the repository manually by accessing ```http://localhost:7200/webapi``` 
   on your browser. Under ```Repository Management```, use the```POST``` endpoint to upload the ```/setup/repo-config.ttl``` file.
5. Make sure the ```pepper/``` directory is on the python path, e.g. by invoking python with
     ```> PYTHON_PATH='path/to/pepper' python path/to/app```
   or by adjusting the python path in your IDE.
6. Start any Application in ```pepper/apps/..```
7. Done
8. Start/Stop Docker by running `docker-compose start/stop` when stopping/restarting the application.

Pepper Troubleshooting
----------------------
> No Pepper-laptop connection can be established

1. Make sure Pepper and the laptop are on the same network
2. Verify Pepper has access to network (by pressing belly-button)
3. Make sure ```ip``` and ```port``` are set correctly in the ```[pepper.framework.backend.naoqi]``` section of ```config/pepper.config``` or ```config/default.config```

> Pepper cannot connect to network

1. Connect Pepper to network using ethernet cable
2. Press belly-button to obtain IP and update ```ip``` in the ```[pepper.framework.backend.naoqi]``` section of ```config/pepper.config``` accordingly
3. Go to robot web page (by entering IP in browser)
4. Go to network settings and connect to wifi
    - If unlisted, reboot robot (and wifi). Make sure wifi is online before robot is.
5. Shutdown robot, remove ethernet cable, and boot again. It now should work...

> Problems with speech audio

1. Start an application with StatisticsComponent and look at the STT (Speech to Text) activity
2. If no signal (i.e ```STT [..........]```):
     ```use_system_microphone``` is set to false  in the ```[pepper.framework.backend.naoqi]``` section of ```config/default.config``` and not overriden from ```config/pepper.config```
    2. Make sure external mic, if used, is switched on and sensitive enough (use OS settings)
    3. Make sure Pepper mic, if used, is not broken?
3. If signal is low (i.e ```STT [|||.......]``` is below ```[pepper.framework.sensors.vad.webrtc] -> threshold```):
    1. Make sure you talk loud enough (noisy fans in Peppers head make it difficult)
    2. Make sure you talk in the right microphone (i.e. ```[pepper.framework.backend.naoqi] -> use_system_microphone```)
    3. Make sure the external mics volume is high enough!
4. If signal is too high (i.e. ```STT [||||||||||]```) all the time:
    1. Peppers own mics cannot handle very loud/noisy environments, like fairs
    2. Use a microphone attached to the laptop, instead!
        - don't forget to override ```[pepper.framework.backend.naoqi] -> use_system_microphone``` in ```config/pepper.config``` and set it to ```True```
5. Microphone should process audio at 16 kHz  (i.e. Statistics: ```Mic 16.0 kHz```), if not:
    1. Override ```cam_resolution``` and/or ```cam_frame_rate``` in the ```[DEFAULT]``` section of ```config/pepper.config``` with lower values in order to meet performance requirements
