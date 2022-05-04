#include <os/log.h>
#include <os/object.h>

#include "Python.h"

PyDoc_STRVAR(_pyoslog_doc,
             "Send messages to the macOS unified logging system. See: "
             "https://developer.apple.com/documentation/os/os_log");

/* -------------------------------------------------------------------------- */

PyDoc_STRVAR(os_log_with_type_doc,
             "Sends a message at a specific logging level, such as default, "
             "info, debug, error, or fault, to the logging system. See: "
             "https://developer.apple.com/documentation/os/os_log_with_type");

static PyObject *py_os_log_with_type(PyObject *self, PyObject *args) {
  PyObject *py_log;
  const uint8_t *type;
  const char *log_message;

  if (!PyArg_ParseTuple(args, "Obs", &py_log, &type, &log_message)) {
    return NULL;
  }

  os_log_t *log;
  int use_default = 0;
  if (PyCapsule_IsValid(py_log, "os_log_t")) {
    if (!(log = (os_log_t *)PyCapsule_GetPointer(py_log, "os_log_t"))) {
      return NULL;
    }
  } else {
    // a hack - treat capsule errors as selecting the default log,
    // meaning we don't have to provide a constant os_log_t object
    use_default = 1;
  }

  // TODO: can we support custom formats here? (must be constant strings)
  os_log_with_type(use_default ? OS_LOG_DEFAULT : *log, (os_log_type_t)type,
                   "%{public}s", log_message);
  Py_RETURN_NONE;
}

static void os_log_release(PyObject *args) {
  os_log_t *log;
  if (!(log = (os_log_t *)PyCapsule_GetPointer(args, "os_log_t"))) {
    return;
  }

  os_release(*log);
  PyMem_Free(log);
}

PyDoc_STRVAR(
    os_log_create_doc,
    "Creates a custom log object. See: "
    "https://developer.apple.com/documentation/os/1643744-os_log_create");

static PyObject *py_os_log_create(PyObject *self, PyObject *args) {
  const char *subsystem;
  const char *category;
  if (!PyArg_ParseTuple(args, "ss", &subsystem, &category)) {
    return NULL;
  }

  os_log_t *log = (os_log_t *)PyMem_Malloc(sizeof(os_log_t *));
  if (log == NULL) {
    return NULL;
  }

  *log = os_log_create(subsystem, category);
  return PyCapsule_New(log, "os_log_t", os_log_release);
}

// TODO: are there any additional methods worth implementing?
// https://opensource.apple.com/source/xnu/xnu-3789.21.4/libkern/os/log.h.auto.html
static PyMethodDef module_methods[] = {
    {.ml_name = "os_log_with_type",
     .ml_meth = (PyCFunction)py_os_log_with_type,
     .ml_flags = METH_VARARGS,
     .ml_doc = os_log_with_type_doc},
    {.ml_name = "os_log_create",
     .ml_meth = (PyCFunction)py_os_log_create,
     .ml_flags = METH_VARARGS,
     .ml_doc = os_log_create_doc},
    {.ml_name = NULL} /* sentinel */
};

static struct PyModuleDef module_definition = {.m_base = PyModuleDef_HEAD_INIT,
                                               .m_name = "_pyoslog",
                                               .m_doc = _pyoslog_doc,
                                               .m_size = -1,
                                               .m_methods = module_methods,
                                               /* m_reload = */ NULL,
                                               .m_traverse = NULL,
                                               .m_clear = NULL,
                                               .m_free = NULL};

PyObject *PyInit__pyoslog(void) {
  PyObject *module = PyModule_Create(&module_definition);
  if (module == NULL) {
    return NULL;
  }

  // the default log type (no named subsystem or facility)
  // see note above for why we don't use the actual value
  PyModule_AddIntConstant(module, "OS_LOG_DEFAULT", 0);

  // standard log types
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_DEFAULT", OS_LOG_TYPE_DEFAULT);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_INFO", OS_LOG_TYPE_DEFAULT);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_DEBUG", OS_LOG_TYPE_DEBUG);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_ERROR", OS_LOG_TYPE_ERROR);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_FAULT", OS_LOG_TYPE_FAULT);

  return module;
}
