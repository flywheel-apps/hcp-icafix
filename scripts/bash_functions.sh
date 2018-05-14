#needed to clean up some of the numerical config options (if empty or non-numerical, output empty)
#optional second input = number of decimal places (Default = 15)
print_decimal_number () { dec=$(echo $2 15 | awk '{print $1}'); echo $1 | awk '{if($1*1 == $1) printf "%.'${dec}'f\n", $1; else print ""}'; };
timestamp () { date +"%Y-%m-%d %H:%M:%S %Z"; }
toupper() { echo "$@" | tr '[:lower:]' '[:upper:]'; };
tolower() { echo "$@" | tr '[:upper:]' '[:lower:]'; };