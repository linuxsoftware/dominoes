#!/bin/bash
if [ $# == 0 ]; then
    dominoes_init_db tests/test_gamecoordinator/tests.ini
    ./setup.py test
else
    for PKG in $(ls -d -1 tests/test_*); do
        PKG=$(basename $PKG)
        for MODULE in $(grep -l $1 tests/$PKG/*.py 2>/dev/null); do
            MODULE=$(basename $MODULE)
            MODULE=${MODULE%.py}
            echo "./setup.py test -s tests.$PKG.$MODULE.$1"
            ./setup.py test -s tests.$PKG.$MODULE.$1
        done
    done
fi
