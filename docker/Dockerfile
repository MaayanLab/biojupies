FROM ubuntu:17.10

COPY pkglist.txt .
RUN apt-get update && apt-get install -y $(cat pkglist.txt)

COPY requirements.R /
RUN Rscript requirements.R

COPY requirements.txt /
RUN pip3 install -r requirements.txt
RUN pip3 install multiprocess

RUN mkdir /notebooks /library /download;
COPY download_libraries.py /
RUN python3 download_libraries.py;
COPY launch.py /
COPY jupyter_notebooks /notebooks

WORKDIR /notebooks
ENTRYPOINT python3 /launch.py; jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --notebook-dir='/notebooks' --NotebookApp.iopub_data_rate_limit=10000000000 --NotebookApp.token=;