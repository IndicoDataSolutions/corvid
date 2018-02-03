#!/bin/bash

(docker build --tag results_extraction .) &&
(docker run --rm results_extraction pytest tests/)