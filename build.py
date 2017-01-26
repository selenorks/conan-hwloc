from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()#
    if platform.system() == "Windows":
        builder.add_common_builds(shared_option_name="hwloc:shared")
        #builder.add_common_builds()
        filtered_builds = []
        for settings, options in builder.builds:
            if settings["compiler"] == "Visual Studio" and settings["compiler.version"] == "14" and settings["compiler.runtime"].startswith("MD") and settings["arch"].startswith("x86"):
                 filtered_builds.append([settings, options])
        builder.builds = filtered_builds
        #builder.add({"arch": "x86_64", "build_type": "Release"}, {"hwloc:shared": "ON"})

    if platform.system() == "Linux":
        builder.add_common_builds()
        filtered_builds = []
        for settings, options in builder.builds:
            if settings["compiler"] == "gcc":
                 filtered_builds.append([settings, options])
        builder.builds = filtered_builds

    builder.run()
