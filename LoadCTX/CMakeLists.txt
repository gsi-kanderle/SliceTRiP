#-----------------------------------------------------------------------------
set(MODULE_NAME LoadCTX)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_NAME}Lib/__init__
  ${MODULE_NAME}Lib/LoadCTXBinfo
  ${MODULE_NAME}Lib/LoadCTXImageImportFromArray
  ${MODULE_NAME}Lib/ctx
  ${MODULE_NAME}Lib/cube
  ${MODULE_NAME}Lib/error
  ${MODULE_NAME}Lib/header
  ${MODULE_NAME}Lib/SubjectHiearchy
  )

set(MODULE_PYTHON_RESOURCES
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()

