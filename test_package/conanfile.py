from conans.model.conan_file import ConanFile
from conans import CMake
import os

############### CONFIGURE THESE VALUES ##################
default_user = "selenorks"
default_channel = "testing"
#########################################################

channel = os.getenv("CONAN_CHANNEL", default_channel)
username = os.getenv("CONAN_USERNAME", default_user)

class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = "hwloc/1.11.5@%s/%s" % (username, channel)

    def build(self):
        if not (self.settings.os == "iOS" or self.settings.os == "Android"):
            cmake = CMake(self.settings)
            self.run('cmake %s %s' % (self.conanfile_directory, cmake.command_line))
            self.run("cmake --build . %s" % cmake.build_config)
        
    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):
        if not (self.settings.os == "iOS" or self.settings.os == "Android"):
            self.run("cd bin && .%smain" % os.sep)
