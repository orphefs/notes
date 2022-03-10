# Configuring `act` to run a github test workflow locally, using an Azure secret key

## Objective

The objective of this short tutorial is to run a Github test workflow on our local machine to speed up development iterations. This is of particular importance when you don't want to pollute Git history by committing a lot of code whose purpose is to get the test workflow to pass. In our case, this is especially important, as our tests are data-intensive and incur large bandwidth overhead on our Azure instance, which translates to higher cost.

We are going to use [act](https://github.com/nektos/act), which is a tool that spawns a docker instance to run the workflow locally. For this to work we will need to do the following:

- Install [Docker Engine](https://docs.docker.com/engine/install/). Please make sure that the Docker daemon is running and functional prior to proceeding with this tutorial.
- Create a `Dockerfile` and build it.
- Create an `.actrc` config file, which tells `act` which linux image to use.
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

Your workflow `.yml` file should contain a line

```bash
on: ${ACTION}
```

The `$ACTION` variable will be passed to the container during runtime, and it is used to specify upon which action (`push`, `pull_request`) the workflow should run.

### `.actrc`

The `.actrc` config file should be in your `Dockerfile` directory.

```bash
cat << EOF > .actrc
-P ubuntu-latest=nektos/act-environments-ubuntu:18.04
EOF
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

## Extra: connecting to Azure passing secret credentials

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

`dind` image:

```bash
docker build -t github-actions-pipeline .
```

Now we can run it using

```bash
sudo docker run \ 
    -d --rm \ # delete container when finished
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd):/project \ # mount repo as volume inside container
    -v $(pwd)/ci-logs:/logs \ # logs directory
    -e ACTION=pull_request \ # our action (could be push, or something else) 
    -e PATH_TO_SECRET=$(pwd)/act.vault
    github-actions-pipeline # our image
```

As mentioned previously, we can view the output on stdout via

```bash
tail -f ci-logs/run.log
```

Happy workflowing :+1:
