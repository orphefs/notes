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
```bash
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
-P ubuntu-latest=node:12.20.1-buster-slim
EOF
```
This specifies which ubuntu image the Dockerfile should use.

### Building time!

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

## Extra: passing secret credentials

Sometimes we are connecting to external services in order to fetch some data. In our case, we have an Azure secret credential which is passed to the workflow using a Github environment variable. It happens to be called `secrets.AZURE_CREDENTIALS`. On Github, this can be set via repository settings menu, available to the administrator.

To use this key locally, we can employ the `--secret-file $PATH_TO_SECRET` flag to tell act to look inside a file where we have stored our secret credential, i.e. `act.vault`. We have to be careful how we store our secret key inside this file, especially if it is a JSON file (check out [this](https://github.com/joho/godotenv) for more details).

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

Rebuild it:
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
