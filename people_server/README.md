# People server

People server is a component that detects people on images.
Sending data to this server is done by using AMQP.

# Installation

Build steps:

    $ mkdir build && cd build
    $ conan install ..
    $ cmake ..
    $ cmake --build .

To start server run executable named `peopleServer`
