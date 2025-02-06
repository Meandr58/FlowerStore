import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myflowerproject.settings")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["flowers"])
    sys.exit(bool(failures))