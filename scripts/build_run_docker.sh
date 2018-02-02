#!/bin/bash

(docker build --tag results_extraction .) &&
(docker run --rm -it results_extraction)