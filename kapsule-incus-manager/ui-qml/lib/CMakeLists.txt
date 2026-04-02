set(LIB_SOURCES
    src/kimclient.cpp
    src/kimclient.h
    src/containersmodel.cpp
    src/containersmodel.h
    src/networksmodel.cpp
    src/networksmodel.h
    src/storagemodel.cpp
    src/storagemodel.h
    src/imagesmodel.cpp
    src/imagesmodel.h
    src/profilesmodel.cpp
    src/profilesmodel.h
    src/eventsource.cpp
    src/eventsource.h
    src/types.h
)

add_library(kim-qt SHARED ${LIB_SOURCES})

target_link_libraries(kim-qt
    PUBLIC
        Qt6::Core
        Qt6::DBus
        Qt6::WebSockets
)

target_include_directories(kim-qt
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:include/kim-qt>
)

set_target_properties(kim-qt PROPERTIES
    VERSION   ${PROJECT_VERSION}
    SOVERSION 0
)

install(TARGETS kim-qt
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES
    src/kimclient.h
    src/types.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/kim-qt
)
