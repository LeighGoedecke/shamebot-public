#!/usr/bin/env bash

#remove old function.qzip before running

deactivate

virtualenv v-env
source v-env/bin/activate
pip3 install -r requirements.txt

cd v-env/lib/python3.7/site-packages
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD

zip -g function.zip lambda_function.py
aws lambda update-function-code --function-name shamebot --zip-file fileb://function.zip --profile leigh-personal