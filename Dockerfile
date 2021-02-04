# Build: docker build -f Dockerfile -t mcs-scene-generator .
# Run: docker run -it mcs-scene-generator bash
#      Then run command like python generate_public_scenes.py -p PREGRAV -t GravitySupportTraining
#      Can map scene folder like this in Docker command: -v ${HOME}/generated_scenes:/mcs-scene-generator/FOLDER/ and
#      then use command parameter -p FOLDER/PREFIX to generate scenes in that folder, i.e.
#           mkdir ~/generated_scenes || true
#           docker run -it -v ${HOME}/generated_scenes:/mcs-scene-generator/FOLDER/ mcs-scene-generator bash
#           python generate_public_scenes.py -p FOLDER/PREFIX -t GravitySupportTraining
#      and then find the generated scenes in ~/generated_scenes.

FROM mcs-playroom-cpu

LABEL maintainer="Next Century Corporation"

ADD . /mcs-scene-generator
# Alternative: RUN git clone https://github.com/NextCenturyCorporation/mcs-scene-generator.git
WORKDIR /mcs-scene-generator

# Install dependencies and run unit tests
RUN python3 -m pip install -r requirements.txt && python -m pytest -vv
