#ifndef WRAP_PTC_H
#define WRAP_PTC_H

#include "Python.h"

#ifdef __cplusplus
extern "C"
{
#endif

namespace wrap_ptc
{
  //~ void initptc(void);
  PyMODINIT_FUNC PyInit_ptc(void);
  //~ PyMODINIT_FUNC PyInit_libptc_orbit(void);
  //~ PyObject* getBasePTCType(char* name);
  PyObject* getBasePTCType(const char* name);
  void initPTC_Map(PyObject* module);
}

#ifdef __cplusplus
}
#endif

#endif // WRAP_PTC_H
