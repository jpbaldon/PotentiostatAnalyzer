cmake_minimum_required(VERSION 3.16)
project(HybridApp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Find Qt6 Widgets and Charts modules
find_package(Qt6 REQUIRED COMPONENTS Widgets Charts)

add_executable(HybridApp
    main.cpp
    mainwindow.cpp
    mainwindow.h
)

target_link_libraries(HybridApp
    PRIVATE Qt6::Widgets Qt6::Charts
)