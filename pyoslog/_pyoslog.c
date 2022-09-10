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
  int type;
  const char *log_message;

  // automatically sets an exception on failure
  if (!PyArg_ParseTuple(args, "Ois", &py_log, &type, &log_message)) {
    return NULL;
  }

  os_log_t *log;
  int type_error = 0;
  int log_disabled = 0;
  if (PyCapsule_IsValid(py_log, "os_log_t")) {
    if (!(log = (os_log_t *)PyCapsule_GetPointer(py_log, "os_log_t"))) {
      type_error = 1;
    }
  } else {
    if (py_log == Py_None) {
      log_disabled = 1;
    } else {
      type_error = 1;
    }
  }

  if (type_error) {
    PyErr_SetString(PyExc_TypeError,
                    "invalid log_object - must be pyoslog.OS_LOG_DEFAULT, "
                    "pyoslog.OS_LOG_DISABLED (== None), or an object "
                    "initialised with os_log_create");
    return NULL;
  }

  os_log_type_t log_type = (os_log_type_t)type;
  switch (log_type) {
  case OS_LOG_TYPE_DEFAULT:
  case OS_LOG_TYPE_INFO:
  case OS_LOG_TYPE_DEBUG:
  case OS_LOG_TYPE_ERROR:
  case OS_LOG_TYPE_FAULT:
    break;
  default:
    PyErr_SetString(
        PyExc_TypeError,
        "invalid log_type - must be one of pyoslog.OS_LOG_TYPE_DEFAULT, "
        "pyoslog.OS_LOG_TYPE_INFO, pyoslog.OS_LOG_TYPE_DEBUG, "
        "pyoslog.OS_LOG_TYPE_ERROR or pyoslog.OS_LOG_TYPE_FAULT");
    return NULL;
  }

  // TODO: can we support custom formats here? (must be constant strings)
  // note: empty string logging is no issue, and the platform automatically
  // truncates messages >= 1024 characters
  os_log_with_type(log_disabled ? OS_LOG_DISABLED : *log, log_type,
                   "%{public}s", log_message);
  Py_RETURN_NONE;
}

PyDoc_STRVAR(
    os_log_type_enabled_doc,
    "Returns a Boolean value that indicates whether the log can "
    "write messages with the specified log type. See: "
    "https://developer.apple.com/documentation/os/1643749-os_log_type_enabled");

static PyObject *py_os_log_type_enabled(PyObject *self, PyObject *args) {
  PyObject *py_log;
  int type;

  // automatically sets an exception on failure
  if (!PyArg_ParseTuple(args, "Oi", &py_log, &type)) {
    return NULL;
  }

  os_log_t *log;
  int type_error = 0;
  int log_disabled = 0;
  if (PyCapsule_IsValid(py_log, "os_log_t")) {
    if (!(log = (os_log_t *)PyCapsule_GetPointer(py_log, "os_log_t"))) {
      type_error = 1;
    }
  } else {
    if (py_log == Py_None) {
      log_disabled = 1;
    } else {
      type_error = 1;
    }
  }

  if (type_error) {
    PyErr_SetString(PyExc_TypeError,
                    "invalid log_object - must be pyoslog.OS_LOG_DEFAULT, "
                    "pyoslog.OS_LOG_DISABLED (== None), or an object "
                    "initialised with pyoslog.os_log_create");
    return NULL;
  }

  os_log_type_t log_type = (os_log_type_t)type;
  switch (log_type) {
  case OS_LOG_TYPE_DEFAULT:
  case OS_LOG_TYPE_INFO:
  case OS_LOG_TYPE_DEBUG:
  case OS_LOG_TYPE_ERROR:
  case OS_LOG_TYPE_FAULT:
    break;
  default:
    PyErr_SetString(
        PyExc_TypeError,
        "invalid log_type - must be one of pyoslog.OS_LOG_TYPE_DEFAULT, "
        "pyoslog.OS_LOG_TYPE_INFO, pyoslog.OS_LOG_TYPE_DEBUG, "
        "pyoslog.OS_LOG_TYPE_ERROR or pyoslog.OS_LOG_TYPE_FAULT");
    return NULL;
  }

  if (os_log_type_enabled(log_disabled ? OS_LOG_DISABLED : *log, log_type)) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}

static void os_log_release(PyObject *args) {
  os_log_t *log;
  if (!(log = (os_log_t *)PyCapsule_GetPointer(args, "os_log_t"))) {
    return;
  }

  if (*log != OS_LOG_DEFAULT) {
    os_release(*log);
  }
  PyMem_Free(log);
}

PyDoc_STRVAR(
    os_log_create_doc,
    "Creates a custom log object. See: "
    "https://developer.apple.com/documentation/os/1643744-os_log_create");

static PyObject *py_os_log_create(PyObject *self, PyObject *args) {
  const char *subsystem;
  const char *category;

  // automatically sets an exception on failure
  if (!PyArg_ParseTuple(args, "ss", &subsystem, &category)) {
    return NULL;
  }

  // subsystem length > 249 characters leads to error messages about read
  // failures and no category value
  int subsystem_length = strlen(subsystem);
  if (subsystem_length <= 0) {
    PyErr_SetString(PyExc_ValueError, "subsystem string must not be empty");
    return NULL;
  }
  if (subsystem_length > 249) {
    PyErr_SetString(
        PyExc_ValueError,
        "subsystem string must be less than 250 characters in length");
    return NULL;
  }

  // category length > 254 characters leads to overflow and no category value
  int category_length = strlen(category);
  if (category_length <= 0) {
    PyErr_SetString(PyExc_ValueError, "category string must not be empty");
    return NULL;
  }
  if (category_length > 254) {
    PyErr_SetString(
        PyExc_ValueError,
        "category string must be less than 254 characters in length");
    return NULL;
  }

  os_log_t *log = (os_log_t *)PyMem_Malloc(sizeof(os_log_t *));
  if (log == NULL) {
    return PyErr_NoMemory();
  }

  *log = os_log_create(subsystem, category);
  return PyCapsule_New(log, "os_log_t", os_log_release);
}

// allow use of the OS_LOG_DEFAULT object
static PyObject *py__get_os_log_default(PyObject *self, PyObject *args) {
  // automatically sets an exception on failure (no arguments expected)
  if (!PyArg_ParseTuple(args, "")) {
    return NULL;
  }

  os_log_t *log = (os_log_t *)PyMem_Malloc(sizeof(os_log_t *));
  if (log == NULL) {
    return PyErr_NoMemory();
  }
  *log = OS_LOG_DEFAULT;
  return PyCapsule_New(log, "os_log_t", os_log_release);
}

// TODO: are there any additional methods worth implementing?
// https://opensource.apple.com/source/xnu/xnu-3789.21.4/libkern/os/log.h.auto.html
static PyMethodDef module_methods[] = {
    {.ml_name = "os_log_with_type",
     .ml_meth = (PyCFunction)py_os_log_with_type,
     .ml_flags = METH_VARARGS,
     .ml_doc = os_log_with_type_doc},
    {.ml_name = "os_log_type_enabled",
     .ml_meth = (PyCFunction)py_os_log_type_enabled,
     .ml_flags = METH_VARARGS,
     .ml_doc = os_log_type_enabled_doc},
    {.ml_name = "os_log_create",
     .ml_meth = (PyCFunction)py_os_log_create,
     .ml_flags = METH_VARARGS,
     .ml_doc = os_log_create_doc},
    {.ml_name = "_get_os_log_default",
     .ml_meth = (PyCFunction)py__get_os_log_default,
     .ml_flags = METH_VARARGS,
     .ml_doc = NULL},
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
  // automatically sets an exception on failure
  PyObject *module = PyModule_Create(&module_definition);
  if (module == NULL) {
    return NULL;
  }

  // standard log types
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_DEFAULT", OS_LOG_TYPE_DEFAULT);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_INFO", OS_LOG_TYPE_INFO);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_DEBUG", OS_LOG_TYPE_DEBUG);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_ERROR", OS_LOG_TYPE_ERROR);
  PyModule_AddIntConstant(module, "OS_LOG_TYPE_FAULT", OS_LOG_TYPE_FAULT);

  return module;
}
