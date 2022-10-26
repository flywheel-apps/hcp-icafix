# Creates docker container that runs HCP Pipeline algorithms
#
#

# Use Ubuntu 14.04 LTS
FROM ubuntu:trusty-20170817

MAINTAINER Flywheel <support@flywheel.io>

# Install packages
RUN apt-get update \
    && apt-get install -y \
    lsb-core \
    bsdtar \
    zip \
    unzip \
    gzip \
    curl \
    jq \
    python-pip

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
#
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9 && \
    echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list.d/cran-rstudio.list && \
    apt-get update && \
    apt-get install -y --force-yes --no-install-recommends r-base-core r-base-dev && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \

# ORDER OF INSTALLATION IS IMPORTANT
RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile


########## 'kernlab' version 0.9.24
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/kernlab/kernlab_0.9-24.tar.gz", repos=NULL, type="source")' \
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/devtools/devtools_2.3.0.tar.gz", repos=NULL, type="source")'

############ 'ROCR' version 1.0.7
RUN Rscript -e 'install.packages("bitops", dependencies=TRUE)'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/caTools/caTools_1.17.1.4.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("gplots", dependencies=TRUE)'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/ROCR/ROCR_1.0-7.tar.gz", repos=NULL, type="source")'


########### #'class' version 7.3.14
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/class/class_7.3-14.tar.gz", repos=NULL, type="source")'

######### #'party' version 1.0.25
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/mvtnorm/mvtnorm_1.0-2.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/survival/survival_2.37-7.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/mvtnorm/mvtnorm_1.0-7.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/survival/survival_2.37-7.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/Matrix/Matrix_1.2-18.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/Rcpp/Rcpp_1.0.7.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/RcppEigen/RcppEigen_0.3.3.9.1.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/nloptr/nloptr_1.0.4.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/nlme/nlme_3.1-147.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/boot/boot_1.3-25.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("minqa", dependencies=TRUE)'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/lme4/lme4_1.1-27.1.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/mratios/mratios_1.4.0.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/TH.data/TH.data_1.0-10.tar.gz", repos=NULL, type="source")' \

RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/zoo/zoo_1.8-8.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/sandwich/sandwich_3.0-0.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/multcomp/multcomp_1.3-8.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/modeltools/modeltools_0.2-21.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/coin/coin_1.1-0.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/strucchange/strucchange_1.5-1.tar.gz", repos=NULL, type="source")'
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/party/party_1.0-25.tar.gz", repos=NULL, type="source")'

###### 'e1071' version 1.6.7
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/e1071/e1071_1.6-7.tar.gz", repos=NULL, type="source")'


########## 'randomForest' version 4.6.12
RUN Rscript -e 'install.packages("https://cran.r-project.org/src/contrib/Archive/randomForest/randomForest_4.6-12.tar.gz", repos=NULL, type="source")'



#

#############################################
# Download and install FSL ICA-FIX

RUN apt-get -y update && \
    apt-get install -y wget && \
    wget -nv http://www.fmrib.ox.ac.uk/~steve/ftp/fix1.066.tar.gz -O /fix.tar.gz && \
    mkdir -p /tmp/fix && \
    cd /tmp/fix && \
    tar zxvf /fix.tar.gz --exclude="compiled/"  --exclude="MCRInstaller.zip" && \
    mv /tmp/fix/fix* /opt/fix && \
    rm /fix.tar.gz && \
    cd / && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV FSL_FIXDIR=/opt/fix

# Download and install Matlab Compiler Runtime v8.5 (2015a)
# Install the MCR dependencies and some things we'll need and download the MCR
# from Mathworks -silently install it
# See http://www.mathworks.com/products/compiler/mcr/ for more info.
# Adapted from https://github.com/flywheel-apps/matlab-mcr
RUN apt-get -qq update && apt-get -qq install -y \
    unzip \
    xorg \
    wget \
    curl && \
    mkdir /mcr-install && \
    mkdir /opt/mcr && \
    cd /mcr-install && \
    wget -nv http://www.mathworks.com/supportfiles/downloads/R2015a/deployment_files/R2015a/installers/glnxa64/MCR_R2015a_glnxa64_installer.zip && \
    cd /mcr-install && \
    unzip -q MCR_R2015a_glnxa64_installer.zip && \
    ./install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    cd / && \
    rm -rf mcr-install

#ENV LD_LIBRARY_PATH /opt/mcr/v85/runtime/glnxa64:/opt/mcr/v85/bin/glnxa64:/opt/mcr/v85/sys/os/glnxa64 #skip this
ENV XAPPLRESDIR /opt/mcr/v85/X11/app-defaults

#############################################
# Download and install FSL 5.0.9

#Build-time key retrieval is sometimes unable to connect to keyserver.  Instead, download the public key manually and store it in plaintext
#within repo.  You should run these commands occassionally to make sure the saved public key is up to date:
#gpg --keyserver hkp://pgp.mit.edu:80  --recv 0xA5D32F012649A5A9 && \
#gpg --export --armor 0xA5D32F012649A5A9 > neurodebian_pgpkey.txt && \
#gpg --batch --yes --delete-keys 0xA5D32F012649A5A9

COPY neurodebian_pgpkey.txt /tmp/

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    echo "deb http://neurodeb.pirsquared.org data main contrib non-free" > /etc/apt/sources.list.d/neurodebian.sources.list && \
    echo "#deb-src http://neurodeb.pirsquared.org data main contrib non-free" >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    echo "deb http://neurodeb.pirsquared.org trusty main contrib non-free" >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    echo "#deb-src http://neurodeb.pirsquared.org trusty main contrib non-free" >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key add /tmp/neurodebian_pgpkey.txt && \
    apt-get update && \
    apt-get install -y dc && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

## Install FSL 5.0.10
WORKDIR /opt/
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py && \
        chmod +x fslinstaller.py && \
        python3 fslinstaller.py -q -d /usr/local/fsl -V 5.0.10

# Configure FSL environment
ENV FSLDIR=/usr/local/fsl
ENV FSL_DIR="${FSLDIR}"
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/usr/local/fsl/bin:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=/usr/local/fsl/
ENV LD_LIBRARY_PATH=/usr/local/fsl/lib:$LD_LIBRARY_PATH
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLOUTPUTTYPE=NIFTI_GZ

#############################################
# Download and install Connectome Workbench
RUN apt-get update && apt-get -y install connectome-workbench=1.2.3-1~nd14.04+1

ENV CARET7DIR=/usr/bin

#############################################
# Download and install HCP Pipelines

#latest v3.x = v3.22.0
#latest v4.x = v4.0.0-alpha.5
#Need to use this 2017-08-24 commit to fix bugs in v4.0.0-alpha.5: 90b0766636ba83f06c9198206cc7fa90117b0b11
RUN apt-get -y update && \
    apt-get install -y wget && \
    apt-get install -y --no-install-recommends python-numpy && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/
RUN wget -nv https://github.com/Washington-University/Pipelines/archive/90b0766636ba83f06c9198206cc7fa90117b0b11.tar.gz -O pipelines.tar.gz && \
    tar zxvf pipelines.tar.gz && \
    rm pipelines.tar.gz && \
    mv /opt/*ipelines* /opt/HCP-Pipelines

ENV HCPPIPEDIR=/opt/HCP-Pipelines

# Manual patche for hcp_fix, re-compiled PostFix and RSS, etc.
COPY pipeline_patch/ ${HCPPIPEDIR}/

# Manual patch for settings.sh and re-compiled FIX
COPY fix_patch/ ${FSL_FIXDIR}/

#############################################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Copy executable/manifest to Gear
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json

# Copy additional scripts and scenes
COPY scripts/*.sh scripts/*.bat ${FLYWHEEL}/scripts/

# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

# Configure entrypoint
ENTRYPOINT ["/flywheel/v0/run"]
