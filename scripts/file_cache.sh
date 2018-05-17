#!/bin/bash

#file_cache.sh -list DIRNAME > cache1.txt generates a list of all files in DIRNAME with modification timestamps
#file_cache.sh -list DIRNAME > cache2.txt generates a list of all files in DIRNAME with modification timestamps (after modifying some files)
#file_cache.sh -diff cache1.txt cache2.txt > oldfiles.txt prints out all files from cache1.txt that HAVEN'T been updated

if [ "$1" = "-list" ]; then
  basedir=$2
  find ${basedir}/ -type f -printf "%T+\t%p\n" | sort
  exit 0
elif [ "$1" = "-diff" ]; then
  origfile=$2
  curfile=$3
  tmpd=`mktemp -d`
  newfile=$tmpd/newfiles.txt
  oldfile=$tmpd/oldfiles.txt
  diff ${curfile} ${origfile} | grep -E '^<' | sed -E 's/^< //' | sort > ${newfile}
  diff ${curfile} ${newfile} | grep -E '^<' | awk -F"\t" '{print $2}' 
  rm -rf $tmpd
  exit 0
fi
