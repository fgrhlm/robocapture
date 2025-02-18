#!/bin/bash

sphinx-apidoc -o source/ ../src && make html
