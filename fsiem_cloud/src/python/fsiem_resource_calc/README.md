# fsiem-resource-calc

A python calculator that estimates needed resources given the number of
licensed seats.

## Build

To make a build and extract compiled binary runs these commands

```bash
cd src/python
# Build
export DOCKER_UBUNTU_VERSION=22.04
sudo -E ./script/run-build-resource-calc.sh
```

This will build the resource_calc binary, plus run confirmation on the output
and then will copy to fsiem-deploy container.

### FAQ

**Q:** I changed this calc, do I need to do anything else? <br/>
**A:** Yes, you need to update `calc.py` with a new version and a date of this change
       and run the above script `sudo -E ./script/run-build-resource-calc.sh`

**Q:** Can I create a binary to run on Windows? <br/>
**A:** Yes, for that you need to compile it on Windows, that is you need to run
       `pyinstaller` on Windows. What you cannot do is to compile the project on Linux
       with the idea of targeting Windows. Linux builds make Linux executables,
       Windows builds make executables for Windows.

**Q:** Why don't you use Alpine to build this? <br/>
**A:** Alpine was the first choice, however it uses a different C runtime than our deploy
       Ubuntu OS. Alpine uses slimmer musl c runtime, Ubuntu uses glibc. Code linked
       against musl is not compatible with glibc, this is why we now compile on Ubuntu.

**Q:** How do I get a shell into this container? <br/>
**A:** On your local machine run

    cd src/python
    # Export the current Ubuntu version, see build/versions.yaml
    export DOCKER_UBUNTU_VERSION=22.04
    sudo -E docker-compose build --progress=plain fsiem-resource-calc
    sudo -E docker-compose run --entrypoint bash fsiem-resource-calc

    # Then do whatever you want, e.g.
    pyinstaller main.spec

    ls -alh dist

    # Successful call
    ./dist/fsiem_resource_calc -s 5 -t clickhouse

    # Prints out:
    {"shards": 1, "replicas": 2, "data_workers": 2, "keeper_workers": 1,
    "super_instance_types": ["c6i.4xlarge", "c5.4xlarge", "c4.4xlarge"],
    "worker_instance_types": ["c6i.2xlarge", "c5.2xlarge", "c4.2xlarge"],
    "keeper_instance_types": [], "cmdb_iops": 3000, "cmdb_throughput": 200,
    "opt_iops": 3000, "opt_throughput": 200,
    "data_disk_throughput": 200, "app_server_mem_gb": 5, "number_of_seats": 5}

    echo "Exit code: $?"

    # Error call
    ./dist/fsiem_resource_calc --seats 1
    echo "Exit code: $?"

**Q:** What is a main.spec file? <br/>
**A:** This file is a specification for the `pyinstaller` to create a self contained
       binary executable file.

**Q:** Can I generate a new spec file? <br/>
**A:** Yes, run a command like

    pyi-makespec --strip --name fsiem_resource_calc --onefile main.py

    # Note, you would want to remove some of the binaries that are not required
    # in runtime, but are stilled bundled. For this edit generated spec file and add

    exclude = ["libssl", "liblzma", "libexpat", "libcrypto", "libbz2",
               "libmpdec", "libz"]
    a.binaries = [x for x in a.binaries if not x[0].startswith(tuple(exclude))]

**Q:** My binary has changed in size, can I make it smaller? <br/>
**A:** This can be an update, when libraries change a version number can change in the
       name of the ignored library. And a library that we do not need and used to ignore,
       is now included in the executable. To see the actual libraries,
       we need to rebuild an executable, but rather than building 1 file, we need to build
       one folder, so we can inspect the library names:

    # bash into the container
    pyinstaller --onedir main.py
    echo "List of libraries for review, some can be excluded in main.spec file"
    ls -alh dist/main
