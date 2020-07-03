=====
TestMgmt
=====

TestMgmt is a Django app to conduct Web-based polls. For each question,
visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "TestMgmt" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'TestMgmt',
    ]

2. Include the TestMgmt URLconf in your project urls.py like this::

    path('TestMgmt/', include('TestMgmt.urls')),

3. Run `python manage.py migrate` to create the TestMgmt models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a TestMgmt (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/TestMgmt/ to participate in the poll.