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
    echo "zipping logs..."
    cd /flywheel/v0/output
    zip -r /tmp/logs.zip ${logdir}
  fi
  echo -e "Cleaning up $1"
  rm -rf "$out_dir/*"
  if [[ -e /tmp/logs.zip ]]; then
    mv /tmp/logs.zip ${out_dir}
  fi
}
