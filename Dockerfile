# Creates docker container that runs HCP Pipeline algorithms
#
#

# Use Ubuntu 14.04 LTS
FROM flywheel/hcp-base:0.1.0-dev

LABEL maintainer="Flywheel <support@flywheel.io>"


# Set up specific environment variables for the HCP Pipeline
ENV FSL_DIR="${FSLDIR}"
ENV HCPPIPEDIR=/opt/HCP-Pipelines
ENV MSMBINDIR=${HCPPIPEDIR}/MSMBinaries
ENV MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
#ENV MATLAB_COMPILER_RUNTIME=/media/myelin/brainmappers/HardDrives/1TB/MATLAB_Runtime/v901
#ENV FSL_FIXDIR=/media/myelin/aahana/fix1.06


#############################################
# Setup FIX, including MATLAB and R

#############################################
# Download and install R and necessary packages

#From https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX/UserGuide
#R version >=3.3.0
#'kernlab' version 0.9.24
#'ROCR' version 1.0.7
#'class' version 7.3.14
#'party' version 1.0.25
#'e1071' version 1.6.7
#'randomForest' version 4.6.12

#RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9 && \
#    echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list.d/cran-rstudio.list && \
#    apt-get update && \
#    apt-get install -force-yes --no-install-recommends r-base-core=3.3.1-* r-base-dev=3.3.1-* && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#RUN echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list.d/cran-rstudio.list && \
#    apt-get update && \
#    apt-get install -force-yes --no-install-recommends r-base-core=3.3.1-* r-base-dev=3.3.1-* && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#




RUN apt-get install -y software-properties-common && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 && \
    add-apt-repository 'deb http://cran.rstudio.com/bin/linux/ubuntu xenial/'  && \
    apt-get update

RUN apt-get install -y --no-install-recommends --allow-unauthenticated r-base-core=3.4.4-*  r-base-dev=3.4.4-*

RUN apt-get install -y build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev



RUN Rscript -e 'install.packages("devtools",dependencies = TRUE)'
RUN Rscript -e 'require(devtools);install_version("kernlab",version = "0.9-24", repos="http://cran.us.r-project.org")'
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

RUN FSL_FIX_R_CMD=` which R `

##### Possible:
#sudo apt-get install r-base r-cran-devtools

#Then on either Linux:

#require(devtools)
#chooseCRANmirror()
#install_version("kernlab", version="0.9-24")
#install_version("ROCR", version="1.0-7")
#install_version("class", version="7.3-14")
#install_version("mvtnorm", version="1.0.8")
#install_version("multcomp", version="1.4-8")
#install_version("coin", version="1.2.2")
#install_version("party", version="1.0-25")
#install_version("e1071", version="1.6-7")
#install_version("randomForest", version="4.6-12")



#############################################
# Download and install FSL ICA-FIX
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get install keyboard-configuration
RUN apt-get -y update && \
    apt-get install -y wget && \
    wget -nv http://www.fmrib.ox.ac.uk/~steve/ftp/fix-1.06.12.tar.gz -O /fix.tar.gz && \
    mkdir -p /tmp/fix && \
    cd /tmp/fix && \
    tar zxvf /fix.tar.gz && \
    mv /tmp/fix/fix* /opt/fix && \
    rm /fix.tar.gz && \
    cd / && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV FSL_FIXDIR=/opt/fix

# Download and install Matlab Compiler Runtime v8.5 (2017b)
# Install the MCR dependencies and some things we'll need and download the MCR
# from Mathworks -silently install it
# See http://www.mathworks.com/products/compiler/mcr/ for more info.
# Adapted from https://github.com/flywheel-apps/matlab-mcr

RUN apt-get -qq update && apt-get -qq install -y \
    unzip \
    xorg \
    curl && \
    mkdir /mcr-install && \
    mkdir /opt/mcr && \
    cd /mcr-install && \
    wget -nv http://www.mathworks.com/supportfiles/downloads/R2017b/deployment_files/R2017b/installers/glnxa64/MCR_R2017b_glnxa64_installer.zip && \
    cd /mcr-install && \
    unzip -q MCR_R2017b_glnxa64_installer.zip && \
    ./install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    cd / && \
    rm -rf mcr-install

#ENV LD_LIBRARY_PATH /opt/mcr/v85/runtime/glnxa64:/opt/mcr/v85/bin/glnxa64:/opt/mcr/v85/sys/os/glnxa64 #skip this
#ENV XAPPLRESDIR /opt/mcr/v93/X11/app-defaults



# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Install gear dependencies
COPY requirements.txt ${FLYWHEEL}/requirements.txt
RUN apt-get install -y --no-install-recommends \
    gawk \
    python3-pip \
    zip \
    unzip \
    gzip && \
    pip3 install --upgrade pip && \
    apt-get remove -y python3-urllib3 && \
    pip3.5 install -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy executable/manifest to Gear
COPY run.py ${FLYWHEEL}/run.py
COPY utils ${FLYWHEEL}/utils
COPY manifest.json ${FLYWHEEL}/manifest.json

# Copy additional scripts and scenes
COPY scripts /tmp/scripts


# Set up directories for HCP fix
RUN mkdir -p /opt/fmrib/MATLAB
RUN ln -s /opt/mcr /opt/fmrib/MATLAB/MATLAB_Compiler_Runtime


# ENV preservation for Flywheel Engine
RUN python -c 'import os, json; f = open("/tmp/gear_environ.json", "w"); json.dump(dict(os.environ), f)'

#ENV LD_LIBRARY_PATH /opt/mcr/v90/runtime/glnxa64:/opt/mcr/v90/bin/glnxa64:/opt/mcr/v90/sys/os/glnxa64:/opt/mcr/v90/extern/bin/glnxa64
RUN PATH=$PATH:$CARET7DIR

# Configure entrypoint
ENTRYPOINT ["/flywheel/v0/run.py"]