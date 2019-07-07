# lorisattack README

_lorisattack_ is a silly name for a staticsite generator, but that's the name.

It is capable of managing multiple organization _sites_ thorugh django templates internally so that you do not need to change _code_ in order to change a site.




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
