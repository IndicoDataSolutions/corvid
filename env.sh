#!/bin/bash

(docker build --tag corvid .) &&
(docker run --rm corvid pytest tests/) &&
(docker run --rm corvid pylint --disable=R,C,W corvid)
