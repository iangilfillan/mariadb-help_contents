#tests
import tests.test_page as test_page

#required imports
import time
import os

#prepare colours
os.system('')

def get_functions(module) -> list:
    funcs = []
    for name in dir(module):
        item = getattr(module, name)
        if str(item).startswith("<function ") and name.startswith("test_"):
            funcs.append( (name, item) )
    return funcs     

def test_functions(functions: list) -> tuple[int, int]:
    #colours for printing
    cred = '\33[91m'
    cgreen = '\33[32m'
    cend = '\33[0m'
    #
    passed = failed = 0
    for name, func in functions:
        try:
            func()
        except AssertionError:
            failed += 1
            print(f"{cred}{name}: Failed!{cend}")
        else:
            passed += 1
            print(f"{cgreen}{name}: Passed!{cend}")
    #resets colours and adds newline
    print(cend)
    return passed, failed


if __name__ == "__main__":
    #track time
    start = time.perf_counter()
    #funcs
    funcs: list = get_functions(test_page)
    passed, failed = test_functions(funcs)
    #debug
    print(f"{passed} Tests Passed")
    print(f"{failed} Tests Failed", end="\n\n")
    #debug time
    time_taken = time.perf_counter() - start

    print(f"Took {time_taken:.3f}s to run {len(funcs)} tests.", end="")