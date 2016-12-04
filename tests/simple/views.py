import random
# Create your views here.


def test_error1(request):
    raise ValueError(random.random())


def test_error2(request):
    raise ValueError(random.random())
