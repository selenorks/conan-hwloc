from conans import ConanFile, tools
import os
from conans.tools import download, unzip, replace_in_file
from conans import CMake
from subprocess import check_output
import platform

class HWLOCConan(ConanFile):
    name = "hwloc"
    version = "1.11.5"
    ZIP_FOLDER_NAME = "hwloc-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "libudev": [True, False],
        "pci": [True, False],
        "libnuma": [True, False],
        }
    default_options = "shared=False","libudev=False", "pci=False", "libnuma=False"
    exports = ["CMakeLists.txt", "FindHwloc.cmake"]
    url="http://github.com/selenorks/conan-hwloc"
    
    #def system_requirements(self):
    #    self.global_system_requirements=True
    #    if self.settings.os == "Linux":
    #        self.output.warn("'libudev' library is required in your computer. Enter sudo password if required...")
    #        self.run("sudo apt-get install libudev0 libudev0:i386 || true ")
    #        self.run("sudo apt-get install libudev1 libudev1:i386 || true ")
    #        self.run("sudo apt-get install libudev-dev libudev-dev:i386 || true ")
    #        self.run("sudo apt-get install libxml2-dev libxml2-dev:i386 || true ")

    #def conan_info(self):
    #    # We don't want to change the package for each compiler version but
    #    # we need the setting to compile with cmake
    #    # self.info.settings.compiler.version = "any"
    #    if self.settings.os == "Windows":
    #        self.info.settings.build_type = "Release"

    def source(self):
        if self.settings.os == "Windows":
            self.run("git clone https://github.com/selenorks/hwloc.git %s -b  hwloc-1.11.5_vs2015  --depth 1" % self.ZIP_FOLDER_NAME)
        else:
            zip_name = "hwloc.tar.gz"
            major = ".".join(self.version.split(".")[0:2])
            import urllib
            urllib.urlretrieve ("http://www.open-mpi.org/software/hwloc/v%s/downloads/hwloc-%s.tar.gz" % (major, self.version), zip_name)
            unzip(zip_name)
            os.unlink(zip_name)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        if self.settings.os == "Linux" or self.settings.os == "Macos" or self.settings.os == "iOS":
            shared_options = "--enable-shared" if self.options.shared else "--enable-static"
            numa_options = "--enable-libnuma" if self.options.libnuma else "--disable-libnuma"
            udev_options = "--enable-libudev" if self.options.libudev else "--disable-libudev"
            pci_options = "--enable-libpci" if self.options.pci else "--disable-libpci"
            flags = "-m32 " if self.settings.arch == "x86" else ""
            flags += " -mmacosx-version-min=10.7 " if self.settings.os == "Macos" else ""
            flags += " -fPIC "
            flags += " -O3 -g " if str(self.info.settings.build_type) == "Release" else "-O0 -g "
            str(self.info.settings.build_type)
            if self.settings.os == "Macos":
                old_str = 'install_name \$rpath/\$soname'
                new_str = 'install_name \$soname'
                replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)

            opt = ""
            if self.settings.os == "iOS":
                 opt = "--host=arm-apple-darwin"
                 sdk = "iphoneos"
                 arch = self.settings.arch if self.settings.arch != "armv8" else "arm64"
                 host_flags = "-arch %s -miphoneos-version-min=5.0 -isysroot $(xcrun -sdk %s --show-sdk-path)" % (arch, sdk)
                 flags = " -O3 -g " if str(self.info.settings.build_type) == "Release" else "-O0 -g "
                 exports = [ "HOST_FLAGS=\"%s\"" % host_flags,
                     "CHOST=\"arm-apple-darwin\"",
                     "CC=\"$(xcrun -find -sdk %s clang)\"" % (sdk),
                     "CXX=\"$(xcrun -find -sdk %s clang++)\"" % (sdk),
                     "CPP=\"$(xcrun -find -sdk %s cpp)\"" % (sdk),
                     "LDFLAGS=\"%s\"" % host_flags,
                     "CXXFLAGS=\"%s %s\"" % (host_flags, flags),
                     "CFLAGS=\"%s %s\"" % (host_flags, flags)
                     ]

                 self.run("cd %s && %s ./configure %s %s %s %s %s --disable-libxml2" % (self.ZIP_FOLDER_NAME, " ".join(exports), shared_options, numa_options, udev_options, pci_options, opt))
                 print("conf done")
                 self.run("cd %s && %s make" % (self.ZIP_FOLDER_NAME, " ".join(exports)))
#                sdk = "iphoneos"

#                arch_flags = "-arch arm64"
#                host_flags = "{} -miphoneos-version-min=8.0 -isysroot $(xcrun -sdk ${SDK} --show-sdk-path)".format(arch_flags, check_output(["xcrun","-sdk", sdk, "--show-sdk-path"]).strip()))
#
            else:
                 self.run("cd %s && CFLAGS='%s -mstackrealign' ./configure %s %s %s %s --disable-libxml2" % (self.ZIP_FOLDER_NAME, flags, shared_options, numa_options, udev_options, pci_options))
                 self.run("cd %s && make" % self.ZIP_FOLDER_NAME)
        elif self.settings.os == "Windows":
            runtimes = {"MD": "MultiThreadedDLL",
                        "MDd": "MultiThreadedDebugDLL",
                        "MT": "MultiThreaded",
                        "MTd": "MultiThreadedDebug"}
            runtime = runtimes[str(self.settings.compiler.runtime)]
            file_path = "%s/contrib/windows/libhwloc.vcxproj" % self.ZIP_FOLDER_NAME
            # Adjust runtime in project solution
            replace_in_file(file_path, "MultiThreadedDLL", runtime)

            platform, configuration = self.visual_platform_and_config()
            print platform
            msbuild = 'Msbuild.exe hwloc.sln /m /t:libhwloc /p:Configuration=%s;Platform="%s"' % (configuration, platform)
            self.output.info(msbuild)
            self.run("cd %s/contrib/windows/ &&  %s" % (self.ZIP_FOLDER_NAME, msbuild))

    def visual_platform_and_config(self):
        platform = 'x64' if self.settings.arch == 'x86_64' else 'win32'
        build_type = str(self.info.settings.build_type)
        configuration = build_type if self.options.shared else (build_type + "Static")
        return platform, configuration
    
    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
        
        self.copy("FindHwloc.cmake", ".", ".")
        self.copy(pattern="*.h", dst="include", src="%s/include" % (self.ZIP_FOLDER_NAME), keep_path=True)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            platform, configuration = self.visual_platform_and_config()
            src = "%s/contrib/windows/%s/%s" % (self.ZIP_FOLDER_NAME, platform, configuration)
            
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=src, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=src, keep_path=False)

        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                    self.copy(pattern="*.so.*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["hwloc"]
        elif self.settings.os == "Macos":
            self.cpp_info.libs = ['hwloc']
        elif self.settings.os == "Windows":
            if self.options.shared: 
                self.cpp_info.libs = ["libhwloc"]
            else:
                self.cpp_info.libs = ["libhwloc"]
