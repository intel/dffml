#!/usr/bin/env bash
# echo command back and exit on error
set -xe

dffml train all \
  -model tfdnnc \
  -model-epochs 400 \
  -model-steps 4000 \
  -model-predict maintained:int:1 \
  -model-classifications 0 1 \
  -model-location modeldir \
  -model-features \
    authors:int:10 \
    commits:int:10 \
    work:int:10 \
  -sources preprocess=dfpreprocess \
  -source-preprocess-dataflow dataflow.yaml \
  -source-preprocess-no_strict \
  -source-preprocess-record_def URL \
  -source-preprocess-inputs "$(date +'%Y-%m-%d %H:%M')=quarter_start_date" \
  -source-preprocess-features maintained:int:1 \
  -source-preprocess-source mysql \
  -source-preprocess-source-insecure \
  -source-preprocess-source-user user \
  -source-preprocess-source-password pass \
  -source-preprocess-source-db db \
  -source-preprocess-source-key key \
  -source-preprocess-source-records \
    'SELECT `key`, `maintained` FROM `status`' \
  -source-preprocess-source-record \
    'SELECT `key`, `maintained` FROM `status` WHERE `key`=%s' \
  -source-preprocess-source-update \
    'INSERT INTO `status` (`key`, `maintained`) VALUES(%s, %s) ON DUPLICATE KEY UPDATE `maintained`=%s' \
  -source-preprocess-source-features '{"maintained": "maintained"}' \
  -source-preprocess-source-predictions '{}' \
  -log debug
