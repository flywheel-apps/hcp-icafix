#needed to clean up some of the numerical config options (if empty or non-numerical, output empty)
#optional second input = number of decimal places (Default = 15)
print_decimal_number () { dec=$(echo $2 15 | awk '{print $1}'); echo $1 | awk '{if($1*1 == $1) printf "%.'${dec}'f\n", $1; else print ""}'; };
timestamp () { date +"%Y-%m-%d %H:%M:%S %Z"; }
toupper() { echo "$@" | tr '[:lower:]' '[:upper:]'; };
tolower() { echo "$@" | tr '[:upper:]' '[:lower:]'; };
countunique () { echo "$@" | tr " " "\n" | sort -u | wc -w; };
cleanup () {
  out_dir=/flywheel/v0/output/
  logdir=/flywheel/v0/output/logs
  if [[ -d ${logdir} ]]; then
    echo "Zipping logs..."
    cd /flywheel/v0/output
    zip -r /tmp/pipelineLogs.zip ${logdir}
    logs=$(find ./* -name "*log*" -o -name "*Log*" -type f)
    zip /tmp/allLogs.zip ${logs}
  fi
  if [[ -z $1 ]]; then
    echo -e "Cleaning up output directory"
    rm -rf /flywheel/v0/output/*
  else
    echo -e "Preserving output directory contents"
    cd /flywheel/v0/output
    zip -r /tmp/hcp-icafix_output_error.zip ./*
    rm -rf /flywheel/v0/output/*
    mv /tmp/hcp-icafix_output_error.zip .
  fi
  if [[ -e /tmp/pipelineLogs.zip ]]; then
    mv /tmp/*Logs.zip ${out_dir}
  fi
}
