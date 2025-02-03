# set base image as python
FROM python:latest

# add user and set workdir
RUN useradd -ms /bin/bash phoenix
USER phoenix
WORKDIR /home/phoenix

# copy code and python package requirements
COPY main.sh decrypt.py requirements.txt ./

# install the specified packages
RUN pip install -r requirements.txt

# set cmd to main.sh
CMD ["/bin/bash", "main.sh"]