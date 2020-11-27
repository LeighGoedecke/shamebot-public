#!/usr/bin/env bash

zip -g function.zip lambda_function.py
aws lambda update-function-code --function-name shamebot --zip-file fileb://function.zip --profile leigh-personal