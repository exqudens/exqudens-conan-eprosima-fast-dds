import logging
from pathlib import Path
from conans import ConanFile, tools
from conans.util.files import save


required_conan_version = ">=1.50.0"


class ConanConfiguration(ConanFile):
    settings = "arch", "os", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    generators = "cmake_find_package"

    def set_name(self):
        try:
            self.name = Path(__file__).parent.joinpath('name-version.txt').read_text().split(':')[0].strip()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def set_version(self):
        try:
            self.version = Path(__file__).parent.joinpath('name-version.txt').read_text().split(':')[1].strip()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def requirements(self):
        try:
            self.requires('foonathan_memory/0.7.3')
            self.requires('fastcdr/2.1.2')
            self.requires('asio/1.29.0')
            self.requires('tinyxml2/10.0.0')
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def configure(self):
        try:
            self.options['foonathan_memory'].shared = self.options.shared
            self.options['fastcdr'].shared = self.options.shared
            #self.options['asio'].shared = self.options.shared
            self.options['tinyxml2'].shared = self.options.shared
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def generate(self):
        try:
            filename = 'conan-packages.cmake'
            content = ''

            content += 'set("${PROJECT_NAME}_CONAN_PACKAGE_NAMES"\n'
            for dep_name in self.deps_cpp_info.deps:
                content += '    "' + dep_name + '"' + '\n'
            content += ')\n'

            content += 'set("${PROJECT_NAME}_CMAKE_PACKAGE_NAMES"\n'
            for dep_name, dep in self.deps_cpp_info.dependencies:
                content += '    "' + dep.get_name('cmake_find_package') + '" # ' + dep_name + '\n'
            content += ')\n'

            content += 'set("${PROJECT_NAME}_CMAKE_PACKAGE_VERSIONS"\n'
            for dep_name, dep in self.deps_cpp_info.dependencies:
                content += '    "' + str(dep.version) + '" # ' + dep_name + '\n'
            content += ')\n'

            content += 'set("${PROJECT_NAME}_CMAKE_PACKAGE_PATHS"\n'
            for dep_name, dep in self.deps_cpp_info.dependencies:
                content += '    "' + dep.rootpath.replace('\\', '/') + '" # ' + dep_name + '\n'
            content += ')\n'

            save(filename, content)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def imports(self):
        try:
            self.copy(pattern="*.dll", dst="bin", src="bin")
            #self.copy(pattern="*.so", dst="lib", src="lib")
            #self.copy(pattern="*.so.*", dst="lib", src="lib")
            #self.copy(pattern="*.dylib", dst="lib", src="lib")
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def package_info(self):
        try:
            self.cpp_info.names["cmake_find_package"] = "fastcdr"
            self.cpp_info.libs = tools.collect_libs(self)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e


if __name__ == "__main__":
    pass
