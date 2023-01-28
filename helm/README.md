## Deployment

### Development Requirements

You'll need to have the following installed before starting

- [docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/docs/helm/helm_install/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)


### Minikube

Minikube will configure your kubectl in order to access the cluster.

Minikube will need to be started whenever the computer/server is restarted. To that end the `./minikube.service` file is provided for linux distros. It will need to be added to the `/etc/systemd/system` direcotry, and you will then need to run `systemctl enable minikube.service` for minikube to start on boot.

Create a tf_models directory in your home directory as this is where the ML recommendation models will be saved.

### Cloudflare

In order to self host, using the free tier of Cloudflare will help manage the DNS settings.

You need to start by adding your domain name to cloudflare then following this documentation in order to create your cloudflared tunnel: https://developers.cloudflare.com/cloudflare-one/tutorials/many-cfd-one-tunnel

You can stop at the deployment phase of the cloudflare documentation as it will be handled by helm later on.

You will want to add the CNAME records pointed towards your cloudflare tunnel

- `<domain-name>`
- `registry.<domain-name>`
- `grafana.<domain-name>`
- `mongo.<domain-name>`
- `jaeger.<domain-name>`
- `coreui.<domain-name>`
- `develop.<domain-name>`
- `developcoreui.<domain-name>`

### Setting up your environment variables

You will need to create a few different accounts which will identify you and provide access to features like OAuth and emails. In the values.yaml files of this directory, you will need to edit the following `foobar` values:

```
# values.yaml

domainName: truba.news # replace with your domain name

configMap:
  redisQueue: "controller"
  defaultUserId: "1a9c14f8-6610-4793-89b3-128f78d2b720"
  publicVapid: foobar #values generate via the google console, see below
  dockerUser: foobar #Your docker user name
  airtableId: "appXAWgdvcKQpJKiz"
  gmailSenderEmail: "info@truba.news"
  gmailSenderName: "truba news"

secrets:
  #important to note that all secret values must be base 64 encoded
  jwtSecret: foobar # Your choice of value
  mongoUser: foobar # Your choice of value
  mongoPw: foobar # Your choice of value
  googleClientId: foobar # see below
  privateVapid: foobar # see below
  dockerPassword: foobar # Your choice of value
  dockerRegistry: foobar # see below
  dockerConfig: foobar # see below
  airtableApiKey: foobar # see below
  gmailPassword: foobar # see below
```

!!! VERY IMPORTANT !!!
Do not commit the values you replace for the secrets, otherwise you will need to generate new Sengrid, and Google keys since they are compromised. It's useful to have a copy of the values written down somewhere safe.

For each secret you will need the base encoded64 value. For example the ouput of `echo 'linuxhint.com' | base64` is what you'd use for the value `linuxhint.com`


```
htpasswd -nb <your-username> <you-password>
```

Make sure to base encode 64 the value generated with `htpasswd` when setting the value in the values.yaml

In order to send emails, you can create a gmail account and set the `gmailAddress` and `gmailPassword` values. In order for this to work however you will need to [Allow less secure apps to ON](https://myaccount.google.com/lesssecureapps) for the email account you created.

The `airtableId` and `airtableApiKey` values can be used to access a custom airtable from the core services. The can be generated via the Airtable dashboard.

You will want to use the [google api console](https://developers.google.com/identity/protocols/oauth2) in order to use OAuth. Make sure to generate the `publicVapid` config, and the `googleClientId` and `privateVapid` secrets from the console.

In order to generate the `dockerRegistry` value use the regular non-base64 values you chose for the `dockerUser` and `dockerPassword` secrets with the following command

```
docker run --entrypoint htpasswd --rm registry:2 -Bbn <dockerUser> <dockerPassword> | base64
```

In order to generate the `dockerConfig` value use the regular non-base64 values you chose for the secrets `dockerUser`,and `dockerPassword`, as well as the using `domainName` value with the following command:

```
kubectl create secret docker-registry docker-registry --docker-server=registry.<domain-name> --docker-username=<DOCKER_USERNAME> --docker-password=<DOCKER_PASSWORD>
```

This will create a secret in the default namespace, we'll have to read it's value and copy it for our `dockerConfig`

```
kubectl get secret docker-registry -o yaml
```

At the top of the outputted file there should be the following

```
apiVersion: v1
data:
  .dockerconfigjson: <you-dockerConfig-value>
```

## Helm

After configuring the configmap and secret values in the values.yaml file, edit the `Chart.yaml` file to reflect your application `name` add `description`. 

You can start by adding the metrics with the following:

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack
```

After that you can now deploy the application with:

```
helm package . && helm install <your-app-name> ./<your-app-name>-0.1.0.tgz
```

After running the install, you will then need to use the upograde command:

```
helm package . && helm upgrade <your-app-name> ./<your-app-name>-0.1.0.tgz
```

## Debugging

https://kubernetes.io/docs/tasks/debug-application-cluster/
