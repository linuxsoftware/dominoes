#---------------------------------------------------------------------------
# QUnit Extensions
#---------------------------------------------------------------------------

@QExt =
    getTests: ->
        tests = []
        for module in QUnit.config.modules
            for test in module.tests
                tests.push(module.name+":"+test.name)
        return tests

#---------------------------------------------------------------------------
# QUnit callbacks
#---------------------------------------------------------------------------

# Runs once at the very beginning.
QUnit.begin ->
    console.log("Running Test Suite")

# Runs before each module.
QUnit.moduleStart (dtl) ->
    console.group("Module: " + dtl.name)

# Runs before each test.
QUnit.testStart (dtl) ->
    console.group("Test: " + dtl.name)

# Runs once after each assertion.
QUnit.log (dtl) ->
    if not dtl.result
        console.error(dtl.message)

# Runs after each test.
QUnit.testDone (dtl) ->
    console.info("Test: %d failures / %d tests", dtl.failed, dtl.total)
    console.groupEnd()

# Runs after each module.
QUnit.moduleDone (dtl) ->
    console.info("Module: %d failures / %d tests", dtl.failed, dtl.total)
    console.groupEnd()
 
# Runs once at the very end.
QUnit.done (dtl) ->
    console.info("Suite: %d failures / %d tests", dtl.failed, dtl.total)
