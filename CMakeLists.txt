cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/cmake-install" CACHE PATH "..." FORCE)
set(CMAKE_VERBOSE_MAKEFILE "TRUE" CACHE BOOL "..." FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS "TRUE" CACHE BOOL "..." FORCE)

block()
    set(fileName "util.cmake")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../${fileName}")
        file(REMOVE "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}")
        file(DOWNLOAD
            "https://raw.githubusercontent.com/exqudens/exqudens-cmake/master/src/main/cmake/${fileName}"
            "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}"
            EXPECTED_MD5 "28a83be2536fcac622b7cccb48e02229"
            STATUS downloadStatus
        )
        if(NOT "${downloadStatus}" STREQUAL "0;\"No error\"")
            message(FATAL_ERROR "downloadStatus: '${downloadStatus}'")
        endif()
        file(COPY "${CMAKE_CURRENT_BINARY_DIR}/tmp/${fileName}" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/../common")
    endif()
endblock()

include("${CMAKE_CURRENT_BINARY_DIR}/../common/util.cmake")

string(REPLACE "." ";" PRESET_NAME_ELEMENTS "${PRESET_NAME}")
if("msvc-16-x64-x64" IN_LIST "PRESET_NAME_ELEMENTS")
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-x64-toolchain.cmake")
        set_msvc_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            VERSION "16"
            HOST "x64"
            TARGET "x64"
            NO_CACHE "FALSE"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/msvc-16-x64-x64-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan.exe" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
    set(CMAKE_CROSSCOMPILING_EMULATOR "powershell.exe" CACHE STRING "..." FORCE)
elseif("gcc" IN_LIST PRESET_NAME_ELEMENTS)
    if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake")
        find_file(COMPILER_PATH NAMES "gcc" PATHS ENV GCC_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
        set_gnu_toolchain(TOOLCHAIN_CONTENT
            PROCESSOR "x86_64"
            OS "${CMAKE_HOST_SYSTEM_NAME}"
            PATH "${COMPILER_PATH}"
            NO_CACHE "FALSE"
            OUTPUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/../common/gcc-toolchain.cmake"
        )
    endif()
    find_program(CONAN_COMMAND NAMES "conan" PATHS ENV CONAN_PATH ENV PATH REQUIRED NO_CACHE NO_DEFAULT_PATH)
endif()

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/name-version.txt" INFO)
string(REPLACE ":" ";" INFO_LIST "${INFO}")
list(GET INFO_LIST 0 RAW_NAME)
list(GET INFO_LIST 1 RAW_VERSION)
string(STRIP "${RAW_NAME}" NAME)
string(STRIP "${RAW_VERSION}" VERSION)
project("${NAME}" VERSION "${VERSION}" LANGUAGES "NONE")

message("project: '${PROJECT_NAME}-${PROJECT_VERSION}'")

enable_language("C")
enable_language("CXX")
include("GenerateExportHeader")
enable_testing()
include("GoogleTest")

set(CMAKE_OBJECT_PATH_MAX 1000)
set(CMAKE_SHARED_LIBRARY_PREFIX "")
set(CMAKE_SHARED_MODULE_PREFIX "")
set(CMAKE_STATIC_LIBRARY_PREFIX "")
set(CMAKE_IMPORT_LIBRARY_PREFIX "")
set(CMAKE_STAGING_PREFIX "")
set(CMAKE_FIND_LIBRARY_PREFIXES "" "lib")
set(CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH FALSE)
set(CMAKE_FIND_USE_CMAKE_SYSTEM_PATH FALSE)
set(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH TRUE)
set(CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY FALSE)
set(CMAKE_FIND_USE_PACKAGE_REGISTRY FALSE)
set(CMAKE_FIND_USE_PACKAGE_ROOT_PATH FALSE)
set(CMAKE_FIND_USE_CMAKE_PATH TRUE)
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG FALSE)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS FALSE)
set(CMAKE_BUILD_RPATH "\$ORIGIN")
set(CMAKE_INSTALL_RPATH "\$ORIGIN")
set(CMAKE_SKIP_BUILD_RPATH TRUE)
set(CMAKE_BUILD_RPATH_USE_ORIGIN TRUE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)
set(CMAKE_CXX_VISIBILITY_PRESET "hidden")
set(CMAKE_VISIBILITY_INLINES_HIDDEN TRUE)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

separate_arguments(CMAKE_CXX_FLAGS NATIVE_COMMAND "${CMAKE_CXX_FLAGS}")
if(MSVC)
    if(NOT "/EHa" IN_LIST CMAKE_CXX_FLAGS AND "/EHsc" IN_LIST CMAKE_CXX_FLAGS)
        list(REMOVE_ITEM CMAKE_CXX_FLAGS "/EHsc")
        list(APPEND CMAKE_CXX_FLAGS "/EHa")
    endif()
endif()
string(JOIN " " CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS})

set_conan_architecture(CONAN_ARCH "${CMAKE_SYSTEM_PROCESSOR}")
set_conan_compiler(CONAN_COMPILER "${CMAKE_CXX_COMPILER_ID}")
set_conan_compiler_version(CONAN_COMPILER_VERSION "${CMAKE_CXX_COMPILER_ID}" "${CMAKE_CXX_COMPILER_VERSION}" MAX_ELEMENTS "1")
set_conan_compiler_runtime(CONAN_COMPILER_RUNTIME "${CMAKE_MSVC_RUNTIME_LIBRARY}")

set_python_boolean(CONAN_INTERFACE_ONLY "${INTERFACE_ONLY}")
set_python_boolean(CONAN_BUILD_SHARED_LIBS "${BUILD_SHARED_LIBS}")

set_conan_settings(CONAN_SETTINGS
    "arch=${CONAN_ARCH}"
    "os=${CMAKE_SYSTEM_NAME}"
    "compiler=${CONAN_COMPILER}"
    "compiler.version=${CONAN_COMPILER_VERSION}"
    "compiler.runtime=${CONAN_COMPILER_RUNTIME}"
    "compiler.libcxx=${CONAN_COMPILER_LIBCXX}"
    "build_type=${CMAKE_BUILD_TYPE}"
)
set_conan_options(CONAN_OPTIONS
    "shared=${CONAN_BUILD_SHARED_LIBS}"
)

cmake_path(CONVERT "$ENV{CMAKE_USER_HOME}" TO_CMAKE_PATH_LIST CMAKE_USER_HOME NORMALIZE)
if("" STREQUAL "${CMAKE_USER_HOME}")
    cmake_path(CONVERT "$ENV{HOME}" TO_CMAKE_PATH_LIST HOME NORMALIZE)
else()
    set(HOME "${CMAKE_USER_HOME}")
endif()
if(NOT EXISTS "${HOME}" OR NOT IS_DIRECTORY "${HOME}")
    message(FATAL_ERROR "HOME: '${HOME}' not exists or not directory.")
endif()
set(CMAKE_HOME "${HOME}/.cmake")
if(NOT EXISTS "${CMAKE_HOME}")
    file(MAKE_DIRECTORY "${CMAKE_HOME}")
endif()
if(NOT EXISTS "${CMAKE_HOME}" OR NOT IS_DIRECTORY "${CMAKE_HOME}")
    message(FATAL_ERROR "CMAKE_HOME: '${CMAKE_HOME}' not exists or not directory.")
endif()
set(CMAKE_DOWNLOADS "${CMAKE_HOME}/downloads")
if(NOT EXISTS "${CMAKE_DOWNLOADS}")
    file(MAKE_DIRECTORY "${CMAKE_DOWNLOADS}")
endif()
if(NOT EXISTS "${CMAKE_DOWNLOADS}" OR NOT IS_DIRECTORY "${CMAKE_DOWNLOADS}")
    message(FATAL_ERROR "CMAKE_DOWNLOADS: '${CMAKE_DOWNLOADS}' is not directory.")
endif()
if(NOT EXISTS "${CMAKE_DOWNLOADS}/${PROJECT_NAME}-${PROJECT_VERSION}.zip")
    message("download ...")
    file(MAKE_DIRECTORY "${PROJECT_BINARY_DIR}/tmp")
    file(DOWNLOAD
        "https://github.com/eProsima/Fast-DDS/archive/refs/tags/v${PROJECT_VERSION}.zip"
        "${PROJECT_BINARY_DIR}/tmp/${PROJECT_NAME}-${PROJECT_VERSION}.zip"
        EXPECTED_MD5 "8fb4b58cfbc45de1c5a86fa6040e28ca"
        STATUS downloadStatus
    )
    if(NOT "${downloadStatus}" STREQUAL "0;\"No error\"")
        message(FATAL_ERROR "downloadStatus: '${downloadStatus}'")
    endif()
    file(COPY "${PROJECT_BINARY_DIR}/tmp/${PROJECT_NAME}-${PROJECT_VERSION}.zip" DESTINATION "${CMAKE_DOWNLOADS}")
    message("... done")
endif()
if(NOT EXISTS "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.zip")
    message("copy from downloads ...")
    file(COPY "${CMAKE_DOWNLOADS}/${PROJECT_NAME}-${PROJECT_VERSION}.zip" DESTINATION "${PROJECT_BINARY_DIR}")
    message("... done")
endif()
if(NOT EXISTS "Fast-DDS-${PROJECT_VERSION}")
    message("extract ...")
    file(ARCHIVE_EXTRACT INPUT "${PROJECT_BINARY_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.zip")
    message("... done")
endif()
get_filename_component("PROJECT_BINARY_DIR_NAME" "${PROJECT_BINARY_DIR}" NAME)
get_filename_component("PROJECT_BINARY_DIR_PARENT" "${PROJECT_BINARY_DIR}" DIRECTORY)
get_filename_component("PROJECT_BINARY_DIR_PARENT_NAME" "${PROJECT_BINARY_DIR_PARENT}" NAME)

set(CONAN_INSTALL_PREFIX "${PROJECT_BINARY_DIR}/conan-install")

file(MAKE_DIRECTORY "${CONAN_INSTALL_PREFIX}/bin")
file(MAKE_DIRECTORY "${CONAN_INSTALL_PREFIX}/lib")

if(NOT EXISTS "${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
    execute_process(
        COMMAND "${CONAN_COMMAND}" "install"
        "--install-folder" "${CONAN_INSTALL_PREFIX}"
        ${CONAN_SETTINGS}
        ${CONAN_OPTIONS}
        "${PROJECT_SOURCE_DIR}/conanfile.py"
        COMMAND_ECHO "STDERR"
        ENCODING "UTF-8"
        COMMAND_ERROR_IS_FATAL ANY
    )
endif()
if(NOT EXISTS "${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
    message(FATAL_ERROR "Not exists: '${CONAN_INSTALL_PREFIX}/conan-packages.cmake'")
endif()
include("${CONAN_INSTALL_PREFIX}/conan-packages.cmake")
list(APPEND CMAKE_MODULE_PATH "${CONAN_INSTALL_PREFIX}")
foreach(
    conanPackageName
    cmakePackageName
    cmakePackageVersion
    cmakePackagePath
    IN ZIP_LISTS
    "${PROJECT_NAME}_CONAN_PACKAGE_NAMES"
    "${PROJECT_NAME}_CMAKE_PACKAGE_NAMES"
    "${PROJECT_NAME}_CMAKE_PACKAGE_VERSIONS"
    "${PROJECT_NAME}_CMAKE_PACKAGE_PATHS"
)
    if(
        "" STREQUAL "${conanPackageName}"
        OR "" STREQUAL "${cmakePackageName}"
        OR "" STREQUAL "${cmakePackageVersion}"
        OR "" STREQUAL "${cmakePackagePath}"
    )
        string(JOIN " " errorMessage
            "Empty value 'conanPackageName': '${conanPackageName}'"
            "or 'cmakePackageName': '${cmakePackageName}'"
            "or 'cmakePackageVersion': '${cmakePackageVersion}'"
            "or 'cmakePackagePath': '${cmakePackagePath}'!"
        )
        message(FATAL_ERROR "${errorMessage}")
    elseif(NOT IS_DIRECTORY "${cmakePackagePath}")
        message(FATAL_ERROR "Not is directory 'cmakePackagePath': '${cmakePackagePath}'!")
    endif()

    if("${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION}" STREQUAL "")
        if("foonathan_memory" STREQUAL "${cmakePackageName}")
            string(REPLACE "." ";" cmakePackageVersionList "${cmakePackageVersion}")
            list(GET "cmakePackageVersionList" "0" cmakePackageVersionMajor)
            list(GET "cmakePackageVersionList" "1" cmakePackageVersionMinor)
            set("${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION" "${cmakePackageVersionMajor}.${cmakePackageVersionMinor}")
        elseif("fastcdr" STREQUAL "${cmakePackageName}")
            string(REPLACE "." ";" cmakePackageVersionList "${cmakePackageVersion}")
            list(GET "cmakePackageVersionList" "0" cmakePackageVersionMajor)
            list(GET "cmakePackageVersionList" "1" cmakePackageVersionMinor)
            set("${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION" "${cmakePackageVersionMajor}.${cmakePackageVersionMinor}")
        else()
            set("${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION" "${cmakePackageVersion}")
        endif()
    endif()

    if("${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_PATH}" STREQUAL "")
        set("${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_PATH" "${cmakePackagePath}")
    endif()

    list(APPEND CMAKE_PREFIX_PATH "${cmakePackagePath}")
endforeach()

if("${${PROJECT_NAME}_CMAKE_FIND_PACKAGE_NAMES}" STREQUAL "")
    list(APPEND "${PROJECT_NAME}_CMAKE_FIND_PACKAGE_NAMES"
        "foonathan_memory"
        "fastcdr"
        "asio"
        "tinyxml2"
    )
endif()
message("${PROJECT_NAME}_CMAKE_FIND_PACKAGE_NAMES:")
foreach(cmakePackageName IN LISTS "${PROJECT_NAME}_CMAKE_FIND_PACKAGE_NAMES")
    message("  ${cmakePackageName}")
endforeach()
unset(NOT_FOUND_PACKAGE_NAMES)
foreach(cmakePackageName IN LISTS "${PROJECT_NAME}_CMAKE_FIND_PACKAGE_NAMES")
    if("foonathan_memory" STREQUAL "${cmakePackageName}")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION}" EXACT QUIET)
    elseif("fastcdr" STREQUAL "${cmakePackageName}")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION}" EXACT QUIET)
    elseif("asio" STREQUAL "${cmakePackageName}")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION}" EXACT QUIET)
    elseif("tinyxml2" STREQUAL "${cmakePackageName}")
        list(APPEND NOT_FOUND_PACKAGE_NAMES "${cmakePackageName}")
        find_package("${cmakePackageName}" "${${PROJECT_NAME}_CMAKE_PACKAGE_${cmakePackageName}_VERSION}" EXACT QUIET)
    else()
        message("Ignore cmakePackageName: '${cmakePackageName}'")
    endif()
endforeach()
set_not_found_package_names(NOT_FOUND_PACKAGE_NAMES ${NOT_FOUND_PACKAGE_NAMES})
if(NOT "" STREQUAL "${NOT_FOUND_PACKAGE_NAMES}")
    foreach(package IN LISTS NOT_FOUND_PACKAGE_NAMES)
        message(SEND_ERROR "${package}_FOUND: '${${package}_FOUND}' ${package}_NOT_FOUND_MESSAGE: '${${package}_NOT_FOUND_MESSAGE}'")
    endforeach()
    message(FATAL_ERROR "Some package not found!")
endif()

set(THIRDPARTY "OFF" CACHE STRING "..." FORCE)
set(Asio_FOUND "ON" CACHE STRING "..." FORCE)
set(TinyXML2_FOUND "ON" CACHE STRING "..." FORCE)

add_library(foonathan_memory ALIAS foonathan_memory::foonathan_memory)
add_library(fastcdr ALIAS fastcdr::fastcdr)

add_subdirectory("${PROJECT_BINARY_DIR_PARENT_NAME}/${PROJECT_BINARY_DIR_NAME}/Fast-DDS-${PROJECT_VERSION}")

#[[add_custom_target("cmake-install"
    COMMAND "${CMAKE_COMMAND}" --install "${PROJECT_BINARY_DIR}" --prefix "${CMAKE_INSTALL_PREFIX}/${PROJECT_NAME}"
    DEPENDS "${PROJECT_NAME}"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    USES_TERMINAL
    VERBATIM
)

add_custom_target("conan-export"
    COMMAND "${CONAN_COMMAND}" "export-pkg"
            #"--force"
            "--package-folder" "${CMAKE_INSTALL_PREFIX}/${PROJECT_NAME}"
            ${CONAN_SETTINGS}
            ${CONAN_OPTIONS}
            "${PROJECT_SOURCE_DIR}/conanfile.py"
            #"gitlab-group+gitlab-sub-group+${PROJECT_NAME}/stable"
    DEPENDS "cmake-install"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    VERBATIM
)]]
