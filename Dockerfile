# Creates docker container that runs HCP Pipeline algorithms
# Maintainer: Amy Hegarty (amy.hegarty@colorado.edu)
#

# Use Ubuntu 20.0.4 LTS
FROM flywheel/hcp-base:1.0.3_4.3.0rc1
#
# hcp-base:1.0.3 Install Set:
#   - FSL 6.0.4
#   - Connectome Workbench 1.5.0
#   - HCP Pipelines v4.3.0
#   - Freesurfer 6.0.1
#   - Washington-University/grandunwrap v1.2.0
#   - MSM_HOCR v3


LABEL maintainer="Amy Hegarty <amy.hegarty@colorado.edu>"

# Set up specific environment variables for the HCP Pipeline
ENV FSL_DIR="${FSLDIR}"
ENV HCPPIPEDIR=/opt/HCP-Pipelines
ENV MSMBINDIR=${HCPPIPEDIR}/MSMBinaries
ENV MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
#ENV MATLAB_COMPILER_RUNTIME=/opt/mcr/v93
#ENV FSL_FIXDIR=/opt/fix

#############################################
# CUSTOM ADD: add additional software packages
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		software-properties-common \
        dirmngr \
        ed \
		less \
		locales \
		vim-tiny \
		wget \
		ca-certificates

#############################################
# Download and install R and necessary packages

# Now install R and littler, and create a link for littler in /usr/local/bin
# Default CRAN repo is now set by R itself, and littler knows about it too
# r-cran-docopt is not currently in c2d4u so we install from source
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
         littler \
 		 r-base \
 		 r-base-dev \
 		 r-recommended
RUN ln -s /usr/lib/R/site-library/littler/examples/install.r /usr/local/bin/install.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r
RUN install.r docopt
RUN rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
 	&& rm -rf /var/lib/apt/lists/*

#############################################
# CUSTOM ADD: add additional software packages (needed for R install)
RUN apt update \
    &&  apt-get install -y --no-install-recommends openssl libssl-dev \
    &&  apt install -y --no-install-recommends build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev

#############################################
# CUSTOM ADD: add R packages for fix

RUN Rscript -e 'install.packages("devtools",dependencies = TRUE)'
RUN Rscript -e 'require(devtools);install_version("kernlab",version = "0.9-24", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("caTools",version = "1.17.1.3", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("ROCR",version = "1.0-7", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("class",version = "7.3-14", repos="http://cran.us.r-project.org")'

RUN Rscript -e 'require(devtools);install_version("mvtnorm",version = "1.0-8", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("multcomp", version="1.4-8", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("modeltools", version="0.2-21", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("coin", version="1.2-2", repos="http://cran.us.r-project.org",dependencies=FALSE)'
RUN Rscript -e 'require(devtools);install_version("libcoin",version = "1.0-5", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("strucchange", repos="http://cran.us.r-project.org")'

RUN Rscript -e 'require(devtools);install_version("party",version = "1.0-25", repos="http://cran.us.r-project.org",dependencies=FALSE)'
RUN Rscript -e 'require(devtools);install_version("e1071",version = "1.6-7", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'require(devtools);install_version("randomForest",version = "4.6-12", repos="http://cran.us.r-project.org")'


#############################################
# Update packages (add git in case want to use newer version of fix)

RUN rm -vfR /var/lib/apt/lists/* \
    && apt-get update \
    && apt-get install -y -q --no-install-recommends git

###############################################
### Download and install FSL ICA-FIX
###   - using compiled version of fix (tar.gz), compiled using MCR v9.3

RUN wget http://www.fmrib.ox.ac.uk/~steve/ftp/fix.tar.gz \
    && tar -zxvf fix.tar.gz \
    && fixVersion=1.06.15 \
    && mv fix /opt/fix-${fixVersion} \
    && rm -f /opt/fix \
    && ln -s /opt/fix-${fixVersion} /opt/fix \
    && rm -rf fix.tar.gz

ENV PATH="/opt/fix:$PATH" \
    FSL_FIXDIR=/opt/fix

# edit fix setting.sh - custom locations for R, MCR
RUN sed -i -e 's+FSL_FIX_R_CMD="${FSLDIR}/fslpython/envs/fslpython/bin/R"+FSL_FIX_R_CMD="/opt/fix/bin"+' /opt/fix/settings.sh \
    && sed -i -e 's+FSL_FIX_MCRROOT="/opt/fmrib/MATLAB/MATLAB_Compiler_Runtime"+FSL_FIX_MCRROOT="/opt/mcr"+' /opt/fix/settings.sh

# add HCP-Pipeline paths needed for CIFTI cleaning step of FIX
ENV PATH=$PATH:/opt/workbench/bin_linux64/ \
    FSL_FIX_CIFTIRW=/opt/HCP-Pipelines/global/matlab/ \
    FSL_FIX_WBC=/opt/workbench/bin_linux64/wb_command

# Download and install Matlab Compiler Runtime v9.3 (2017b)
# Install the MCR dependencies and some things we'll need and download the MCR
# from Mathworks -silently install it
# See http://www.mathworks.com/products/compiler/mcr/ for more info.
# Adapted from https://github.com/flywheel-apps/matlab-mcr

#update for possible resolution to java issue -- may not be needed ?
# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Fix certificate issues
RUN apt-get update && \
    apt-get install -y ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

# other packages we need...
RUN apt-get install -y \
      libqt5gui5 \
      apt-file \
    && apt-file update

RUN apt install --reinstall libqt5widgets5 libqt5gui5 libqt5dbus5 libqt5network5 libqt5core5a

RUN apt-get -qq update && apt-get -qq install -y \
    unzip \
    xorg \
    wget \
    curl && \
    mkdir /mcr-install && \
    mkdir /opt/mcr && \
    cd /mcr-install && \
    wget http://ssd.mathworks.com/supportfiles/downloads/R2017b/deployment_files/R2017b/installers/glnxa64/MCR_R2017b_glnxa64_installer.zip && \
    cd /mcr-install && \
    unzip -q MCR_R2017b_glnxa64_installer.zip && \
    ./install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    cd / && \
    rm -rf mcr-install

# rename problematic package
RUN mv /opt/mcr/v93/bin/glnxa64/libmwcoder_types.so /opt/mcr/v93/bin/glnxa64/libmwcoder_types_old.so

# Configure environment variables for MCR
#ENV LD_LIBRARY_PATH /opt/mcr/v93/runtime/glnxa64:/opt/mcr/v93/bin/glnxa64:/opt/mcr/v93/sys/os/glnxa64 # skip this
ENV XAPPLRESDIR /opt/mcr/v93/X11/app-defaults
#
#
######################################################
# FLYWHEEL GEAR STUFF...

# Add poetry oversight.
RUN apt-get update &&\
    apt-get install -y --no-install-recommends \
	software-properties-common &&\
	add-apt-repository -y 'ppa:deadsnakes/ppa' &&\
	apt-get update && \
	apt-get install -y --no-install-recommends python3.9\
    python3.9-dev \
	python3.9-venv \
	python3-pip &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry based on their preferred method. pip install is finnicky.
# Designate the install location, so that you can find it in Docker.
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.6 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive questions
    POETRY_NO_INTERACTION=1 \
    VIRTUAL_ENV=/opt/venv
RUN python3.9 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3.9 -m pip install --upgrade pip && \
    ln -sf /usr/bin/python3.9 /opt/venv/bin/python3
ENV PATH="$POETRY_HOME/bin:$PATH"

# get-poetry respects ENV
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Installing main dependencies
ARG FLYWHEEL=/flywheel/v0
COPY pyproject.toml poetry.lock $FLYWHEEL/
RUN poetry install --no-root --no-dev

## Installing the current project (most likely to change, above layer can be cached)
## Note: poetry requires a README.md to install the current project
COPY run.py manifest.json README.md $FLYWHEEL/
COPY fw_gear_icafix $FLYWHEEL/fw_gear_icafix

# Configure entrypoint
RUN chmod a+x $FLYWHEEL/run.py && \
    echo "hcp-icafix" > /etc/hostname && \
    rm -rf $HOME/.npm

ENTRYPOINT ["poetry","run","python","/flywheel/v0/run.py"]


#####################################################
#   v---OLD---v
#
## Make directory for flywheel spec (v0)
#ENV FLYWHEEL /flywheel/v0
#WORKDIR ${FLYWHEEL}
#
## Install gear dependencies
#COPY requirements.txt ${FLYWHEEL}/requirements.txt
#RUN apt-get install -y --no-install-recommends \
#    gawk \
#    python3-pip \
#    zip \
#    unzip \
#    gzip && \
#    pip3 install --upgrade pip && \
#    apt-get remove -y python3-urllib3 && \
#    pip3.5 install -r requirements.txt && \
#    rm -rf /root/.cache/pip && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
## Copy executable/manifest to Gear
#COPY run.py ${FLYWHEEL}/run.py
#COPY utils ${FLYWHEEL}/utils
#COPY manifest.json ${FLYWHEEL}/manifest.json
#
#
## Set up directories for HCP fix
#RUN mkdir -p /opt/fmrib/MATLAB
#RUN ln -s /opt/mcr /opt/fmrib/MATLAB/MATLAB_Compiler_Runtime
#RUN ln -s /usr/share/fsl/6.0 /opt/fmrib/fsl
#
#ENV HCP_DIR=/flywheel/v0/hcp_dir
#ENV SCRIPT_DIR=/flywheel/v0/scripts/scripts
#ENV SCENE_DIR=/flywheel/v0/scripts/PostFixScenes
#ENV HCP_PIPELINE_DIR=/opt/HCP-Pipelines
#
#ENV MATLAB_COMPILER_RUNTIME=/opt/mcr/v93
#ENV FSL_FIX_MATLAB=/opt/mcr/v93
#ENV FSL_FIX_MATLAB_MODE=0
#ENV FSL_FIX_MCRROOT=/opt/mcr
#ENV FSL_FIX_MCR=/opt/mcr/v93
#ENV FSL_FIX_MCRV=v93
#    # Set up HCP environment variables
#ENV DEFAULT_ENVIRONMENT_SCRIPT=/flywheel/v0/scripts/SetUpHCPPipeline.sh
#ENV DEFAULT_RUN_LOCAL=TRUE
#ENV DEFAULT_FIXDIR=/opt/fix
#
#ENV FSL_FIX_WBC=/opt/workbench/bin_linux64/wb_command
#ENV FSL_FIX_R_CMD=/usr/bin/R
#
## ENV preservation for Flywheel Engine
#ENV PATH=$PATH:$CARET7DIR
#RUN python -c 'import os, json; f = open("/tmp/gear_environ.json", "w"); json.dump(dict(os.environ), f)'
#
##ENV LD_LIBRARY_PATH=/opt/mcr/v93/runtime/glnxa64:/opt/mcr/v93/bin/glnxa64:/opt/mcr/v93/sys/os/glnxa64:/opt/mcr/v93/extern/bin/glnxa64
#
#
## Configure entrypoint
#ENTRYPOINT ["/flywheel/v0/run.py"]
