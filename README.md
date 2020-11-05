# Harbor Python Client

[Harbor](https://goharbor.io/) is an open source registry that secures artifacts with policies and role-based access control, ensures images are scanned and free from vulnerabilities, and signs images as trusted. Harbor, a CNCF Graduated project, delivers compliance, performance, and interoperability to help you consistently and securely manage artifacts across cloud native compute platforms like Kubernetes and Docker.

## Installtion

```bash
pip intasll -r requirements.txt
```

## Usages
* Clean projects or artifacts

``` python
client = HarborClient('<Harbor api base url>', '<username>', '<password>')
client.clean_project('<project name>')
```