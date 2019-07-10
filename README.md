# lorisattack README

_lorisattack_ is a silly name for a django-based staticsite generator, but it needs some name...

_lorisattack_ is capable of managing multiple organization _sites_ through django templates internally so that you do not need to change/commit _code_ in order to update a site.

It targets generating simple websites (index page + news) to be served from an S3 bucket.

NEWS content may be updated by _any_ member of the Organization as defined by the Organization registered `OrganizationEmailDomain`s.


## Defining NewsItems

### Create NewsItem in Admin

1. From `news` application select `NewsItem` and click, `create`.

2. Upload Image

### Define in `template`
A news item takes the form of:

```python

```

NewsItems may be included on the organization's `IndexPage` by including the following in the `IndexPage.template` :

```
<ul>
    {% for newsitem in news_items %}    
        <img src="{{ newsitem.image }}" />  # TODO: update to proper bucket url
        {{ newsitem.title }}
        {{ newsitem.text|truncatechars:15 }} 
    {% endfor %}
</ul>
```

> Where: 
> The `news_items` variable name *must* be the same value as defined by `IndexPage.newsitems_template_variablename`

## Testing

0. Prepare local environment:

    ```bash
    pipenv install --dev
    ```

1. Set the test settings:

    ```bash
    pipenv shell
    export DJANGO_SETTINGS_MODULE=lorisattack.settings.local
 
    # prepare test environment
    docker-compose up -d
    
    # run tests
    # -> Assumes root directory
    cd lorisattack
    python manage.py test
    ```

## CircleCI Integration

In circleCI the following _environment variables_ need to be set in the circleci project:

- AWS_DEFAULT_REGION
    - Region to run the service in
- AWS_ACCESS_ROLE_ARN
    - AWS Execution/Deployment Role
- CIRCLECI_AWS_ACCESS_KEY_ID
    - user aws_access_key_id for circleci deployment   
- CIRCLECI_AWS_SECRET_ACCESS_KEY
    - - user aws_secret_access_kley for circleci deployment 
    