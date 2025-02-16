## Deployment

### Development Requirements

You'll need to have the following installed before starting

- [docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/docs/helm/helm_install/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)


### Microk8s

[microk8s](https://microk8s.io/) will install a small k8s cluster on your local machine accessible via the microk8s command. To use kubectl directly, your can follow this [guide](https://microk8s.io/docs/working-with-kubectl)


### Cloudflare

To self host, using the free tier of Cloudflare will help manage the DNS settings.

You need to start by adding your domain name to cloudflare then following this documentation to create your cloudflared tunnel: https://developers.cloudflare.com/cloudflare-one/tutorials/many-cfd-one-tunnel

After creating your tunnel you will need to add the tunnel credentials to k8s using the following command `kubectl create secret generic tunnel-credentials --from-file=credentials.json=/Users/yourusername/.cloudflared/<tunnel ID>.json`

You can stop at the deployment phase of the cloudflare documentation as it will be handled by helm later on.

You will want to add the CNAME records pointed towards your cloudflare tunnel

- `<domain-name>`
- `grafana.<domain-name>`
- `mongo.<domain-name>`
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
  airtableId: "appXAWgdvcKQpJKiz"
  mailSenderEmail: "info@truba.news"
  mailSenderName: "truba news"

secrets:
  #important to note that all secret values must be base 64 encoded
  jwtSecret: foobar # Your choice of value
  mongoUser: foobar # Your choice of value
  mongoPw: foobar # Your choice of value
  googleClientId: foobar # see below
  privateVapid: foobar # see below
  dockerConfig: foobar # see below
  airtableApiKey: foobar # see below
  mailPassword: foobar # see below
```

!!! VERY IMPORTANT !!!
Do not commit the values you replace for the secrets, otherwise you will need to generate new Sengrid, and Google keys since they are compromised. It's useful to have a copy of the values written down somewhere safe.

For each secret you will need the base encoded64 value. For example the ouput of `echo 'linuxhint.com' | base64` is what you'd use for the value `linuxhint.com`


```
htpasswd -nb <your-username> <you-password>
```

Make sure to base encode 64 the value generated with `htpasswd` when setting the value in the values.yaml

To send emails, you can use the email provider of your choice. The emailing is currently setup with [resend](https://resend.com/). You can create an account and set the `mailAddress` and `mailPassword` values.

The `airtableId` and `airtableApiKey` values can be used to access a custom airtable from the core services. The can be generated via the Airtable dashboard.

You will want to use the [google api console](https://developers.google.com/identity/protocols/oauth2)to use OAuth. Make sure to generate the `publicVapid` config, and the `googleClientId` and `privateVapid` secrets from the console.

To generate the `dockerConfig` value use the following command:

```
kubectl create secret docker-registry docker-registry --docker-server=docker.io --docker-username=<DOCKER_USERNAME> --docker-password=<DOCKER_PASSWORD>
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

## Building images

You need to build the images for all the different services and push them to your docker repository. This can by done from the root of this project using the `docker-compose build <service>` & `docker-compose push <service>` commands. By default it will build and push the development environment images. You can change the environment value to production in the /env file to push the production images.


## Monitoring

To add the log and trace collection you can apply the grafana tools with the following commands.
```
kubectl create namespace grafana
helm install grafana grafana/grafana -n grafana
helm install -n grafana alloy grafana/alloy --values alloy-values.yaml
helm install --values loki-values.yaml loki grafana/loki -n grafana
helm install tempo grafana/tempo -n grafana
```

This will install all the required applications in the grafana namespace. To access the dashboard use the following

```
kubectl get secret --namespace grafana grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
kubectl port-forward --namespace grafana service/grafana 3000:80
```
Then use the retrieved password with the username 'admin' when visiting localhost:3000. You will need to set-up the loki and tempo connections with the following values
```
http://loki-gateway
http://tempo:3100
```

## Debugging

https://kubernetes.io/docs/tasks/debug-application-cluster/
