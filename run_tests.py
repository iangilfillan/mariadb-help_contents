#tests
import tests.test_format as test_format
import tests.test_generate as test_generate

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
    #modules
    modules = [test_format, test_generate]
    #test modules
    total_funcs = 0
    total_passed = total_failed = 0
    for module in modules:
        funcs: list = get_functions(module)
        passed, failed = test_functions(funcs)
        #add totals
        total_funcs += len(funcs)

        total_passed += passed
        total_failed += failed

    #debug
    print(f"{total_passed} Tests Passed")
    print(f"{total_failed} Tests Failed", end="\n\n")
    #debug time
    time_taken = time.perf_counter() - start

    print(f"Took {time_taken:.3f}s to run {total_funcs} tests.", end="")