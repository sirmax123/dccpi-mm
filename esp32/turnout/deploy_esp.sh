#!/usr/bin/env bash

set -ue ${DEBUG:+-x}

UPDATE_EXTERNAL_LIBS=${UPDATE_EXTERNAL_LIBS:+TRUE}
DEPLOY_WWWROOT=${DEPLOY_WWWROOT:+TRUE}
DEPLOY_LIBS=${DEPLOY_LIBS:+TRUE}
DEPLOY_CODE=${DEPLOY_CODE:+TRUE}

## Global variables
PORT="/dev/ttyUSB0"
BOUND="115200"
LIBS="uasyncio concurrent tinyweb"
SIMPLE_LIBS="copy logging types"
AMPY="/usr/local/bin/wb_ampy --port ${PORT} --baud ${BOUND}"
EXT_LIBS="external_libs"


show_deploumant_parameters() {
    echo "***********************************************"
    echo UPDATE_EXTERNAL_LIBS=${UPDATE_EXTERNAL_LIBS}
    echo DEPLOY_WWWROOT=${DEPLOY_WWWROOT}
    echo DEPLOY_LIBS=${DEPLOY_LIBS}
    echo DEPLOY_CODE=${DEPLOY_CODE}
    echo "***********************************************"

}

update_external_libs() {
    # Update library from git repos
    mkdir -p ${EXT_LIBS} && pushd ${EXT_LIBS}
    test -d ${EXT_LIBS}/micropython-lib || \
    git clone https://github.com/micropython/micropython-lib.git
    pushd  micropython-lib && git pull && popd

    test -d tinyweb || \
    git clone https://github.com/belyalov/tinyweb.git
    pushd tinyweb && git pull && popd
    popd
}

#mpfshell -c "open ttyUSB0;  ls ; put lib/test/test.py" -n
deploy_libs() {
    ${AMPY} \
        mkdir --exists-okay lib

    for lib in ${LIBS};
    do
    ${AMPY} \
        mkdir --exists-okay lib/${lib}
    done

    # Deploy uasyncio
    ${AMPY} \
        mkdir --exists-okay lib/uasyncio/websocket

    pushd ${EXT_LIBS}

    ${AMPY} put micropython-lib/uasyncio/uasyncio/__init__.py                          /lib/uasyncio/__init__.py
    ${AMPY} put micropython-lib/uasyncio.core/uasyncio/core.py                         /lib/uasyncio/core.py
    ${AMPY} put micropython-lib/uasyncio.queues/uasyncio/queues.py                     /lib/uasyncio/queues.py
    ${AMPY} put micropython-lib/uasyncio.synchro/uasyncio/synchro.py                   /lib/uasyncio/synchro.py
    ${AMPY} put micropython-lib/uasyncio.websocket.server/uasyncio/websocket/server.py /lib/uasyncio/websocket/server.py


    # deploy concurrent/futures
    ${AMPY} \
        mkdir --exists-okay lib/concurrent/futures

    ${AMPY} put micropython-lib/concurrent.futures/concurrent/futures/__init__.py      /lib/concurrent/futures/__init__.py



    # deploy tinyweb lib
    ${AMPY} put tinyweb/tinyweb/__init__.py /lib/tinyweb/__init__.py
    ${AMPY} put tinyweb/tinyweb/server.py /lib/tinyweb/server.py

    for SIMPLE_LIB in ${SIMPLE_LIBS};
    do
        ${AMPY} put micropython-lib/${SIMPLE_LIB}/${SIMPLE_LIB}.py ${SIMPLE_LIB}.py
    done
    popd
}

deploy_wwwroot() {
    pushd wwwroot
    ${AMPY} \
        mkdir --exists-okay wwwroot
    for F in $(ls -1); do
    ${AMPY} put ${F} wwwroot/${F}
    done
    popd
}

deploy_code() {
    ${AMPY} put boot.py boot.py
    ${AMPY} put main.py main.py
}


show_deploumant_parameters

if [ "${UPDATE_EXTERNAL_LIBS}" == "TRUE" ]; then
    update_external_libs
fi

if [ "${DEPLOY_LIBS}" == "TRUE" ]; then
    deploy_libs
fi

if [ "${DEPLOY_WWWROOT}" == "TRUE" ]; then
    deploy_wwwroot
fi

if [ "${DEPLOY_CODE}" == "TRUE" ]; then
    deploy_code
fi


