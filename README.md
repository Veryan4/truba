![Image of truba](https://truba.news/truba-logo.svg)

# Truba

This is an Open Source news application, built largely in Javascript and Python. The goal of this application is to give users control over their personalization, and to be as transparent as possible while doing so.
https://truba.news

At the same time it aims to provide a boilerplate experience for self-hosting a fullstack application, enabling the rapid ability to do all of the following:

- Have separate environments
- Queue async tasks for service availability
- Monitor & trace services to troubleshoot performance
- Manage users
- Collect user feedback/data
- Scrape external data
- Extract features
- Train & test ML models with Jupyter
- Use the trained ML models for recommendations

### News Sources

A living list of sources that are used can be found [here](https://airtable.com/invite/l?inviteId=invjDxkD4T0H9ypwa&inviteToken=254370034c8d6efff4123af230402ed5f6d03c77492f3bba8bfc7689c5dc32fb&utm_source=email)

### Outlining the Architecture

Monorepo Multibranch Pipeline for CI/CD.

Environments are namespaced, with the Jupyter service pointed on the development envrionment

Communication Diagram: https://docs.google.com/drawings/d/1bK8-KgHAQ7AyQKpqLYPwv1mSkQZ3ThVu2fzXNFTJYQo/edit?usp=sharing

Client facing API docs: https://developcoreui.truba.news/redoc

### How to Deploy a k8s infrastructure

Visit the readme in the `/helm` directory

### How to add a service

- Start by adding a directory to this repo with the name of your service. This service mus contain a Dockerfile which can build the service.
- Edit the `./helm/values.yaml` file by adding a values to the `services`
- From the /helm directory run `helm upgrade <your-app-name> .`

### How to add an environment

Note that a new environment comes packaged with the web, user, socket, core, ml, user services as well as an instance of mongodb and redis. This means that you may need to increase the number of nodes you're using to run your cluster.

- Increase the minimum node count on the environments node poll by 1
- Find the new untainted node with `kubectl get nodes` then `kubectl describe node <node-name>`
- `kubectl label node <node-name> spray=<new-environment-name>`
- `kubectl taint node <node-name> spray=<new-environment-name>:NoSchedule`
- Add the new Environment to the `./helm/values.yaml`
- From the /helm directory run `helm upgrade <your-app-name> .`
