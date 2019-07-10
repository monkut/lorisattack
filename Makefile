flake8:
	pipenv run flake8 --max-line-length 170 --max-complexity 15 --ignore F403,F405,E252,W606 --exclude */migrations/*,*/tests.py,*/tests/* lorisattack/

mypy:
	pipenv run mypy lorisattack/ --disallow-untyped-defs --ignore-missing-imports

test:
	cd lorisattack && pipenv run python manage.py test

test-local:
	docker-compose up -d
	docker-compose run wait
	cd lorisattack && pipenv run python manage.py test || \
		docker-compose down

coverage:
	cd lorisattack && pipenv run coverage run --source '.' manage.py test

check: flake8 mypy
