cmake_minimum_required(VERSION 3.21.0)
project(peopleServer)

set(CMAKE_CXX_STANDARD 17)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# create libINIReader lib, because inih from conan doesn't supply it
add_library(libINIReader
    src/INIReader.cpp
)

add_library(poco_handler_lib
    src/SimplePocoHandler.cpp
)
add_library(people_lib
    src/PeopleDetector.cpp
    src/processRequest.cpp
)

add_executable(peopleServer src/peopleServer.cpp)
target_link_libraries(peopleServer ${CONAN_LIBS} libINIReader poco_handler_lib people_lib)

file(COPY ${CMAKE_SOURCE_DIR}/src/cascades DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
file(COPY ${CMAKE_SOURCE_DIR}/src/config.ini DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
