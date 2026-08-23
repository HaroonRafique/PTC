#include "Python.h"
#include "orbit_mpi.hh"

#include <cstring>
#include <string>

#include "pyORBIT_Object.hh"

#include "cinterface2ptc.hh"

#include "wrap_cinterface2ptc.hh"
#include "wrap_matrix_generator.hh"
#include "wrap_bunch.hh"

using namespace OrbitUtils;

namespace wrap_ptc
{
  void error(const char* msg){ ORBIT_MPI_Finalize(msg); }

#ifdef __cplusplus
extern "C"
{
#endif

//---------------------------------------------------------
// ptc method wrappers
//---------------------------------------------------------

// Main routine to initialize PTC.

static PyObject* wrap_ptc_init_(PyObject *self, PyObject *args)
{
  const char* file_name;
  int length_of_name;
  if(!PyArg_ParseTuple(args, "si:_ptc_init_",
                       &file_name, &length_of_name))
  {
    error("ptc_init_ - cannot parse arguments!");
  }

  cout << "file_name = " << file_name << " Length =" << length_of_name << "\n";

  ptc_init_(file_name, length_of_name);
  Py_INCREF(Py_None);
  return Py_None;
}

// Get initial twiss at entrance of the lattice.

static PyObject* wrap_ptc_get_twiss_init_(PyObject *self, PyObject *args)
{
  double betax;
  double betay;
  double alphax;
  double alphay;
  double etax;
  double etapx;
  double etay;
  double etapy;
  double cox;
  double copx;
  double coy;
  double copy;
  ptc_get_twiss_init_(&betax, &betay, &alphax, &alphay, &etax, &etapx, &etay, &etapy, &cox, &copx, &coy, &copy);
  return Py_BuildValue("(dddddddddddd)", betax, betay, alphax, alphay, etax, etapx, etay, etapy, cox, copx, coy, copy);
}

// Get number of PTC ORBIT nodes, harmonic number,
// length of the ring, and gamma transition.

static PyObject* wrap_ptc_get_ini_params_(PyObject *self, PyObject *args)
{
  int nNodes;
  int nHarm;
  double lRing;
  double gammaT;
  ptc_get_ini_params_(&nNodes, &nHarm, &lRing, &gammaT);
  return Py_BuildValue("(iidd)", nNodes, nHarm, lRing, gammaT);
}

// Get synchronous particle params mass, charge, and energy.

static PyObject* wrap_ptc_get_syncpart_(PyObject *self, PyObject *args)
{
  double mass;
  int charge;
  double kin_energy;
  ptc_get_syncpart_(&mass, &charge, &kin_energy);
  return Py_BuildValue("(did)", mass, charge, kin_energy);
}

// Call ptc method to set up synchronous particle calualtions
// (before and after node).
// This method should be called from PTC_Map instance.
// These methods are located inside PTC (not interfaces).
// If node_index < 0 then PTC will do something inside
// that does not relate to tracking.

static PyObject* wrap_ptc_synchronous_set_(PyObject *self, PyObject *args)
{
  int* node_index;
  if(!PyArg_ParseTuple(args, "i:ptc_synchronous_set_",
                       &node_index))
  {
    error("ptc_synchronous_set_ - cannot parse arguments!");
  }
  ptc_synchronous_set_(node_index);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* wrap_ptc_synchronous_after_(PyObject *self, PyObject *args)
{
  int* node_index;
  if(!PyArg_ParseTuple(args, "i:ptc_synchronous_after_",
                       &node_index))
  {
    error("ptc_synchronous_after_ - cannot parse arguments!");
  }
  ptc_synchronous_after_(node_index);
  Py_INCREF(Py_None);
  return Py_None;
}

// Read the acceleration table into the ptc code.

static PyObject* wrap_ptc_read_accel_table_(PyObject *self, PyObject *args)
{
  const char* file_name;
  int length_of_name;
  if(!PyArg_ParseTuple(args, "si:ptc_read_accel_table_",
                       &file_name, &length_of_name))
  {
    error("ptc_read_accel_table_ - cannot parse arguments!");
  }
  ptc_read_accel_table_(file_name, length_of_name);
  Py_INCREF(Py_None);
  return Py_None;
}

// Get twiss and length for a node with index.

static PyObject* wrap_ptc_get_twiss_for_node_(PyObject *self, PyObject *args)
{
  int node_index;
  double length;
  double betax;
  double betay;
  double alphax;
  double alphay;
  double etax;
  double etapx;
  double etay;
  double etapy;
  double cox;
  double copx;
  double coy;
  double copy;
  if(!PyArg_ParseTuple(args, "i:ptc_get_twiss_for_node_",
                       &node_index))
  {
    error("ptc_get_twiss_for_node_ - cannot parse arguments!");
  }
  ptc_get_twiss_for_node_(&node_index, &length, &betax, &betay,
                          &alphax, &alphay, &etax, &etapx, &etay, &etapy, &cox, &copx, &coy, &copy);
  return Py_BuildValue("(ddddddddddddd)", length,
                       betax, betay, alphax, alphay, etax, etapx, etay, etapy, cox, copx, coy, copy);
}

// Get number of native PTC fibres.

static PyObject* wrap_ptc_get_fibre_count_(PyObject *self, PyObject *args)
{
  int n_fibres = 0;
  int status = 0;
  ptc_get_fibre_count_(&n_fibres, &status);
  return Py_BuildValue("(ii)", status, n_fibres);
}

// Get native PTC fibre name.

static PyObject* wrap_ptc_get_fibre_name_(PyObject *self, PyObject *args)
{
  int fibre_index;
  if(!PyArg_ParseTuple(args, "i:ptc_get_fibre_name_",
                       &fibre_index))
  {
    error("ptc_get_fibre_name_ - cannot parse arguments!");
  }
  const int name_len = 120;
  char fibre_name[name_len + 1];
  std::memset(fibre_name, ' ', name_len);
  fibre_name[name_len] = '\0';
  int status = 0;
  ptc_get_fibre_name_(&fibre_index, fibre_name, &status, name_len);
  std::string name(fibre_name, name_len);
  size_t end = name.find_last_not_of(' ');
  if(end == std::string::npos)
  {
    name.clear();
  }
  else
  {
    name.erase(end + 1);
  }
  return Py_BuildValue("(is)", status, name.c_str());
}

// Get native PTC fibre aperture state.

static PyObject* wrap_ptc_get_fibre_aperture_(PyObject *self, PyObject *args)
{
  int fibre_index;
  if(!PyArg_ParseTuple(args, "i:ptc_get_fibre_aperture_",
                       &fibre_index))
  {
    error("ptc_get_fibre_aperture_ - cannot parse arguments!");
  }
  int kindaper = 0;
  double r[2] = {0.0, 0.0};
  double x = 0.0;
  double y = 0.0;
  double dx = 0.0;
  double dy = 0.0;
  double s = 0.0;
  int status = 0;
  ptc_get_fibre_aperture_(&fibre_index, &kindaper, r, &x, &y, &dx, &dy, &s, &status);
  return Py_BuildValue("(iiddddddd)", status, kindaper, r[0], r[1], x, y, dx, dy, s);
}

// Set native PTC fibre aperture state. This is primarily for tests and
// explicit user-side aperture application.

static PyObject* wrap_ptc_set_fibre_aperture_(PyObject *self, PyObject *args)
{
  int fibre_index;
  int kindaper;
  double r1 = 0.0;
  double r2 = 0.0;
  double x = 0.0;
  double y = 0.0;
  double dx = 0.0;
  double dy = 0.0;
  if(!PyArg_ParseTuple(args, "iidddddd:ptc_set_fibre_aperture_",
                       &fibre_index, &kindaper, &r1, &r2, &x, &y, &dx, &dy))
  {
    error("ptc_set_fibre_aperture_ - cannot parse arguments!");
  }
  double r[2] = {r1, r2};
  int status = 0;
  ptc_set_fibre_aperture_(&fibre_index, &kindaper, r, &x, &y, &dx, &dy, &status);
  return Py_BuildValue("i", status);
}

// Track 6D coordinates through a PTC-ORBIT node.

static PyObject* wrap_ptc_track_particle_(PyObject *self, PyObject *args)
{
  int* node_index;
  double* x;
  double* xp;
  double* y;
  double* yp;
  double* phi;
  double* dE;
  if(!PyArg_ParseTuple(args, "idddddd:ptc_track_particle_",
                       &node_index, &x, &xp, &y, &yp, &phi, &dE))
  {
    error("ptc_track_particle_ - cannot parse arguments!");
  }
  ptc_track_particle_(node_index, x, xp, y, yp, phi, dE);
  Py_INCREF(Py_None);
  return Py_None;
}

// Reads additional ptc commands from file and executes them inside ptc.

static PyObject* wrap_ptc_script_(PyObject *self, PyObject *args)
{
  const char* p_in_file;
  int length_of_name;
  if(!PyArg_ParseTuple(args, "si:ptc_script_",
                       &p_in_file, &length_of_name))
  {
    error("ptc_script_ - cannot parse arguments!");
  }
  ptc_script_(p_in_file, length_of_name);
  Py_INCREF(Py_None);
  return Py_None;
}

//===========================================================
// This method should be called before particle tracking.
// It specifies the type of the task that will be performed
// in ORBIT before particle tracking for particular node.
//   i_task = 0 - do not do anything
//   i_task = 1 - energy of the sync. particle changed
//===========================================================

static PyObject* wrap_ptc_get_task_type_(PyObject *self, PyObject *args)
{
  int* i_node;
  int* i_task;
  if(!PyArg_ParseTuple(args, "ii:ptc_get_task_type_",
                       &i_node, &i_task))
  {
    error("ptc_get_task_type_ - cannot parse arguments!");
  }
  ptc_get_task_type_(i_node, i_task);
  Py_INCREF(Py_None);
  return Py_None;
}

//===================================================
// This returns the lowest frequency of the RF cavities.
// It will be used to transform phi to z[m].
//===================================================

static PyObject* wrap_ptc_get_omega_(PyObject *self, PyObject *args)
{
  double* X;
  if(!PyArg_ParseTuple(args, "d:ptc_get_omega_",
                       &X))
  {
    error("ptc_get_omega_ - cannot parse arguments!");
  }
  ptc_get_omega_(X);
  Py_INCREF(Py_None);
  return Py_None;
}

//===================================================
// trackBunch tracks a bunch of particles using
// ptc_track_particle_.
//===================================================

static PyObject* wrap_ptc_trackBunch(PyObject *self, PyObject *args)
{
  PyObject* pyBunch;
  double PhaseLength;
  int orbit_ptc_node_index;
  if(!PyArg_ParseTuple(args, "Odi:ptc_trackBunch", &pyBunch,
                       &PhaseLength, &orbit_ptc_node_index))
  {
    error("ptc_trackBunch(Bunch* bunch, double PhaseLength, const int &orbit_ptc_node_index) - parameter is needed.");
  }
  PyObject* pyORBIT_Bunch_Type = wrap_orbit_bunch::getBunchType("Bunch");
  if(!PyObject_IsInstance(pyBunch, pyORBIT_Bunch_Type))
  {
    error("ptc_trackBunch(Bunch* bunch, double PhaseLength, const int &orbit_ptc_node_index) - the first parameter should be a Bunch.");
  }
  Bunch* cpp_bunch = (Bunch*) ((pyORBIT_Object*) pyBunch)->cpp_obj;
  ptc_trackBunch(cpp_bunch, PhaseLength, orbit_ptc_node_index);
  Py_INCREF(Py_None);
  return Py_None;
}

//===================================================
// This recalculates the PTC TWISS
//===================================================

static PyObject* wrap_ptc_update_twiss_(PyObject *self, PyObject *args)
{
  ptc_update_twiss_();
  Py_INCREF(Py_None);
  return Py_None;
}

  

static PyMethodDef ptcMethods[] =
{
  {"ptc_init_",               wrap_ptc_init_,               METH_VARARGS, "Initializes PTC"},
  {"ptc_get_twiss_init_",     wrap_ptc_get_twiss_init_,     METH_VARARGS, "Gets entrance twiss parameters"},
  {"ptc_get_ini_params_",     wrap_ptc_get_ini_params_,     METH_VARARGS, "Gets main lattice parameters"},
  {"ptc_get_syncpart_",       wrap_ptc_get_syncpart_,       METH_VARARGS, "Gets synchronous particle parameters"},
  {"ptc_synchronous_set_",    wrap_ptc_synchronous_set_,    METH_VARARGS, "Sets synchronous particle calculations"},
  {"ptc_synchronous_after_",  wrap_ptc_synchronous_after_,  METH_VARARGS, "Completes synchronous particle calculations"},
  {"ptc_read_accel_table_",   wrap_ptc_read_accel_table_,   METH_VARARGS, "Reads acceleration information table"},
  {"ptc_get_twiss_for_node_", wrap_ptc_get_twiss_for_node_, METH_VARARGS, "Twiss parameters at node"},
  {"ptc_get_fibre_count_",    wrap_ptc_get_fibre_count_,    METH_VARARGS, "Gets native PTC fibre count"},
  {"ptc_get_fibre_name_",     wrap_ptc_get_fibre_name_,     METH_VARARGS, "Gets native PTC fibre name"},
  {"ptc_get_fibre_aperture_", wrap_ptc_get_fibre_aperture_, METH_VARARGS, "Gets native PTC fibre aperture"},
  {"ptc_set_fibre_aperture_", wrap_ptc_set_fibre_aperture_, METH_VARARGS, "Sets native PTC fibre aperture"},
  {"ptc_track_particle_",     wrap_ptc_track_particle_,     METH_VARARGS, "Tracks particle through PTC element"},
  {"ptc_script_",             wrap_ptc_script_,             METH_VARARGS, "Additional ptc commands"},
  {"ptc_get_task_type_",      wrap_ptc_get_task_type_,      METH_VARARGS, "Call before tracking"},
  {"ptc_get_omega_",          wrap_ptc_get_omega_,          METH_VARARGS, "Returns fundamental RF frequency"},
  {"ptc_trackBunch",          wrap_ptc_trackBunch,          METH_VARARGS, "Track the Bunch through a PTC element"},
  {"ptc_update_twiss_",       wrap_ptc_update_twiss_,       METH_VARARGS, "Recalculates the PTC TWISS"},
  {NULL, NULL}
};

//--------------------------------------------------
// Initialization of ptc routines.
//--------------------------------------------------

//~ void initlibptc_orbit(void)
//~ {
  //~ PyObject *m, *d;
  //~ m = Py_InitModule((char*)"libptc_orbit", ptcMethods);
  //~ d = PyModule_GetDict(m);
//~ }

PyMODINIT_FUNC PyInit_pylibptc_orbit(void)
{
  static struct PyModuleDef ptc_module_def = {
      PyModuleDef_HEAD_INIT,
      "libptc_orbit",                // Name of the module
      "PTC Python wrapper module",  // Module documentation
      -1,                            // Size of per-interpreter state or -1
      ptcMethods                     // Methods table
  };

  PyObject *m = PyModule_Create(&ptc_module_def);
  if (m == NULL)
  {
    return NULL; // Return NULL on failure
  }

  // Add constants, if needed
  return m; // Return the module object
}

//~ PyObject* getBasePTCType(char* name)
//~ {
  //~ PyObject* mod = PyImport_ImportModule("ptc");
  //~ PyObject* pyType = PyObject_GetAttrString(mod, name);
  //~ Py_DECREF(mod);
  //~ Py_DECREF(pyType);
  //~ return pyType;
//~ }

PyObject* getBasePTCType(const char* name)
{
  PyObject* mod = PyImport_ImportModule("ptc");
  if (mod == NULL)
  {
    PyErr_SetString(PyExc_ImportError, "Failed to import PTC module.");
    return NULL;
  }

  PyObject* pyType = PyObject_GetAttrString(mod, name);
  Py_DECREF(mod);
  if (pyType == NULL)
  {
    PyErr_Format(PyExc_AttributeError, "PTC module has no attribute '%s'", name);
    return NULL;
  }
  return pyType;
}

#ifdef __cplusplus
}
#endif

} //end of namespace wrap_ptc
