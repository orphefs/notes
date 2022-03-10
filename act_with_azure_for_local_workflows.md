# Configuring `act` to run a github test workflow locally, using an Azure secret key

## Objective

The objective of this short tutorial is to run a Github test workflow on our local machine to speed up development iterations. This is of particular importance when you don't want to pollute Git history by committing a lot of code whose purpose is to get the test workflow to pass. In our case, this is especially important, as our tests are data-intensive and incur large bandwidth overhead on our Azure instance, which translates to higher cost.

We are going to use [act](https://github.com/nektos/act), which is a tool that spawns a docker instance to run the workflow locally. For this to work we will need to do the following:

- Install [Docker Engine](https://docs.docker.com/engine/install/). Please make sure that the Docker daemon is running and functional prior to proceeding with this tutorial.
- Create an `.actrc` config file, which tells `act` which linux image to use.
- Create a `Dockerfile` and build it.
- Run the docker image, passing some environment variables needed for the workflow to execute.

Let's start!

## Building the docker image

### Dockerfile

Let us create a *Docker-in-Docker*  `Dockerfile`:

Contents of `Dockerfile`:

```Dockerfile
FROM docker:dind

RUN apk add curl
RUN curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sh

COPY .actrc /
RUN mv /.actrc ~/.actrc

WORKDIR /project

CMD /bin/sh -c "act -n ${ACTION} > /logs/dry-run.log; act ${ACTION} > /logs/run.log"
```

A typical workflow `.yml` file (i.e. `tests.yml`) may look like this:

```yaml
name: Github action to run tests
on: pull_request
jobs:
  Run-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.8"
      - uses: iterative/setup-dvc@v1
      - name: "Install some_dependency"
        run: |
          sudo apt-get install -y some_dependency
      - name: "Install requirements"
        run: pip install -r requirements.txt
      - name: "Pull data"
        run: |
          dvc remote modify my_data_remote url azure://my_data_dir/
          dvc remote modify my_data_remote account_name 'my_account_name'
          dvc pull -f
      - name: "Run tests"
        run: |
          export LD_PRELOAD=/lib/x86_64-linux-gnu/libstdc++.so.6:$LD_PRELOAD
          python -m pytest
```

The line

```yaml
on: ${ACTION}
```

The `$ACTION` variable will be passed to the container during runtime, and it is used to specify upon which action (`push`, `pull_request`) the workflow should run.

### `.actrc`

The `.actrc` config file should be in your `Dockerfile` directory.

Contents of `.actrc`:

```bash
-P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-20.04
```

This specifies which ubuntu image the Dockerfile should use. For more info on available docker images for `act` have a look [here](https://github.com/nektos/act/blob/master/IMAGES.md).

### Building time

Let's build the Dockerfile via

```bash
docker build -t github-actions-pipeline .
```

>NOTE: If you haven't enabled rootless mode, you may have to use `sudo`.

Now you can run `docker images` and see the newly built image.

## Running the docker container

Now we can run our image and look at the logs.

```bash
sudo docker run \ 
    -d --rm \ # delete container when finished
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd):/project \ # mount repo as volume inside container
    -v $(pwd)/ci-logs:/logs \ # logs directory
    -e ACTION=pull_request \ # our action (could be push, or something else) 
    github-actions-pipeline # our image
```

Hopefully, this should now run your workflow. To observe the logs, run

```bash
tail -f ci-logs/run.log
```

## Next steps: passing secret credentials for connecting to external services

Sometimes we are connecting to external services (i.e. [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/))in order to fetch some data. To understand how to set up an Azure AD application and service principal, have a look at [this](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal) tutorial. In our case, we have registered our Github workflow as an app on Azure, and have obtained an Azure secret credential which is passed to the workflow using a Github environment variable. It happens to be called `secrets.AZURE_CREDENTIALS`. On Github, this can be set via repository settings menu, available to the administrator.

Once you have set up your app on Azure and obtained your secret key, then you can also use this key locally. We can employ the `--secret-file $PATH_TO_SECRET` flag to tell act to look inside a file where we have stored our secret credential, i.e. `act.vault`. We have to be careful how we store our secret key inside this file, especially if it is a JSON file (check out [this](https://github.com/joho/godotenv) for more details).

Contents of `act.vault`, which in this case is formatted in `yaml`:

```yaml
AZURE_CREDENTIALS: { "clientId": "redacted", "clientSecret": "redacted",  "subscriptionId": "redacted",   "tenantId": "redacted",  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",  "resourceManagerEndpointUrl": "https://management.azure.com/", "activeDirectoryGraphResourceId": "https://graph.windows.net/",  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",  "galleryEndpointUrl": "https://gallery.azure.com/",   "managementEndpointUrl": "https://management.core.windows.net/" }
```

(...make sure there are no newlines in your JSON!)

Now, let's include the new argument inside `Dockerfile`:

Contents of `Dockerfile`:

```bash
FROM docker:dind

RUN apk add curl
RUN curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sh

COPY .actrc /
RUN mv /.actrc ~/.actrc

WORKDIR /project

CMD /bin/sh -c "act -n ${ACTION} > /logs/dry-run.log; act ${ACTION} --secret-file=${PATH_TO_SECRET} > /logs/run.log"
```

As of the time of writing this, the [Ubuntu 20.04 image](https://github.com/catthehacker/docker_images/pkgs/container/ubuntu) kindly provided by [@catthehacker](https://github.com/catthehacker) does not come with the Azure CLI preinstalled, so we will have to use this image as a base and install `az` on top of it.

Our new image `Dockerfile` will look like this:

```Dockerfile
FROM ghcr.io/catthehacker/ubuntu:act-20.04

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

```

Now, we have to build both the `act` image, and our `dind` image, in the following order:

`act` image:

```bash
docker build -t ubuntu:act-20.04 .
```

We also have to change the contents of our `.actrc` to use the new `act` image in our `dind` container:

Contents of `.actrc`:

```bash
-P ubuntu-latest=ubuntu:act-20.04
```

>NOTE: I have provided a prebuilt image in my [Docker hub repo](https://hub.docker.com/repository/docker/orphefs/orphefs). If you want to use that instead, you can replace the above with `-P ubuntu-latest=orphefs/orphefs:act-ubuntu-20.04` in your `.actrc`

`dind` image:

```bash
docker build -t github-actions-pipeline .
```

We have to put our secret file `act.vault` inside a directory `secret/`

```bash
mkdir secret

```

Our directory structure should now look something like this:

```bash
$ tree -a
.
├── my-repo
│   ├── .git
│   ├── .github
│   │   └── workflows
│   │       └── tests.yml
│   └── src
└── secret
    └── act.vault
```

Now we can run the `dind` container using

```bash
sudo docker run -d --rm \ # delete container when finished
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd)/my-repo:/project \ # mount my-repo into /project inside container
    -v $(pwd)/ci-logs:/logs \ # logs directory
    -v $(pwd)/secret:/secret \ # mount secret/ directory into /secret directory inside container
    -e ACTION=pull_request \ # our action (could be push, or something else) 
    github-actions-pipeline 
```

Hopefully the above runs smoothly and creates a `ci-logs` dir in our folder structure

```bash
$ tree -a
.
├── ci-logs
│   ├── dry-run.log
│   └── run.log
├── my-repo
│   ├── .git
│   ├── .github
│   │   └── workflows
│   │       └── tests.yml
│   └── src
└── secret
    └── act.vault
```

As mentioned previously, we can view the output on stdout via

```bash
tail -f ci-logs/run.log
```

which should look something like this:

```bash
[Github action to run tests/Run-tests]   🐳  docker volume rm act-Github-action-to-run-tests-Run-tests
tail: ci-logs/run.log: file truncated
[Github action to run tests/Run-tests] 🚀  Start image=ubuntu:act-20.04
[Github action to run tests/Run-tests]   🐳  docker pull image=ubuntu:act-20.04 platform= username= forcePull=false
[Github action to run tests/Run-tests]   🐳  docker pull ubuntu:act-20.04
[Github action to run tests/Run-tests]   🐳  docker create image=ubuntu:act-20.04 platform= entrypoint=["/usr/bin/tail" "-f" "/dev/null"] cmd=[]
[Github action to run tests/Run-tests] Created container name=act-Github-action-to-run-tests-Run-tests id=570bea46dc1532498dbb04cdf972b67613407f44b25b0f128dd5970b06d504c9 from image ubuntu:act-20.04 (platform: )
[Github action to run tests/Run-tests] ENV ==> [RUNNER_TOOL_CACHE=/opt/hostedtoolcache RUNNER_OS=Linux RUNNER_TEMP=/tmp]
[Github action to run tests/Run-tests]   🐳  docker run image=ubuntu:act-20.04 platform= entrypoint=["/usr/bin/tail" "-f" "/dev/null"] cmd=[]
.
.
.
[Github action to run tests/Run-tests]   ✅  Success - Run tests
[Github action to run tests/Run-tests] Removed container: 130da0ff0af6c87e2c9061a19af9a2f3e519c15a81ea27b56cf647efba6f26be
[Github action to run tests/Run-tests]   🐳  docker volume rm act-Github-action-to-run-tests-Run-tests
```

Happy workflowing :+1:
