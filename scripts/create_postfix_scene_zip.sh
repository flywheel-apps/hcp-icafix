#!/bin/bash

OUTPUT_DIR=$1
Subject=$2
PostFixName=$3
ZipFileName=$4

cd ${OUTPUT_DIR}

tmpd=`mktemp -d -p .`

${CARET7DIR}/wb_command -zip-scene-file ${Subject}/MNINonLinear/Results/${PostFixName}/${Subject}_${PostFixName}_ICA_Classification_singlescreen.scene \
  ${ZipFileName} \
  ${tmpd}/tmp1_${ZipFileName}.zip \
  -base-dir ${OUTPUT_DIR}

${CARET7DIR}/wb_command -zip-scene-file ${Subject}/MNINonLinear/Results/${PostFixName}/${Subject}_${PostFixName}_ICA_Classification_dualscreen.scene \
  ${ZipFileName} \
  ${tmpd}/tmp2_${ZipFileName}.zip \
  -base-dir ${OUTPUT_DIR}

cd $tmpd
unzip -qq tmp1_${ZipFileName}.zip
unzip -qq -n tmp2_${ZipFileName}.zip
rm -f ${OUTPUT_DIR}/${ZipFileName}.zip
zip -q -r ${OUTPUT_DIR}/${ZipFileName}.zip ${ZipFileName}/

cd ${OUTPUT_DIR}

rm -rf ${tmpd}
