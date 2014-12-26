QuantumMechanic
===============

Interactive simulations of quantum circuits.
Chelsea Voss, 6.845 Fall 2014.


Installation instructions
-------------------------

    apt-get install git gcc python2.7 python2.7-dev python-scipy python-pip ipython texlive imagemagick pdf2svg python-django xzdec
    pip install cython
    pip install qutip
    git clone https://github.com/csvoss/quantummechanic.git
    cd quantummechanic
    echo "SECRET_KEY='whatever'" > quantummechanic/settings_local.py
    tlmgr init-usertree
    tlmgr install standalone
    python manage.py runserver 0.0.0.0:8000 &

Confirmed installable on Debian/jessie.