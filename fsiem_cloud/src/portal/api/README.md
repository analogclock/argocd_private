# FortiSiem SaaS portal API

This project is an API that is used by portal UI. It's written in C# and dotnet core.

## Updates

Updates are executed inside a docker environment.
To update this project's libraries run the following commands:

```bash
# From root of this _repo_, this will update all projects, e.g.
cd ~/git/fsiem_cloud
sudo -E ./build/ci-wrapper.sh update

# OR

# From root of this _project_, this will update just this project, e.g.
cd src/portal/api
sudo ./script/run-update.sh
```
