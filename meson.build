# ext/PTC/meson.build

# Include source and interface directories
ptc_inc_dirs = include_directories('source', 'interface')

# Define Fortran source files
fort_sources = files(
  'source/m_real_polymorph.f90',
  'source/n_complex_polymorph.f90',
  'source/o_tree_element.f90',
  'source/c_dabnew.f90',
  'source/d_lielib.f90',
  'source/h_definition.f90',
  'source/i_tpsa.f90',
  'source/j_tpsalie.f90',
  'source/k_tpsalie_analysis.f90',
  'source/l_complex_taylor.f90',
  'source/a_scratch_size.f90',
  'source/b_da_arrays_all.f90',
  'source/Sq_orbit_ptc.f90',
  'source/Sra_fitting.f90',
  'source/Sr_spin.f90',
  'source/Ss_fake_mad.f90',
  'source/St_pointers.f90',
  'source/Sk_link_list.f90',
  'source/Sl_family.f90',
  'source/Sma0_beam_beam_ptc.f90',
  'source/Sma_multiparticle.f90',
  'source/Sm_tracking.f90',
  'source/Sn_mad_like.f90',
  'source/So_fitting.f90',
  'source/Spb_fake_gino_sub.f90',
  'source/Sp_keywords.f90',
  'source/Se_status.f90',
  'source/Sf_def_all_kinds.f90',
  'source/Sg_sagan_wiggler.f90',
  'source/Sh_def_kind.f90',
  'source/Si_def_element.f90',
  'source/Sa_extend_poly.f90',
  'source/Sb_sagan_pol_arbitrary.f90',
  'source/Sc_euclidean.f90',
  'source/Sd_frame.f90',
  'interface/ptcinterface.f90'
)

# Define object dependencies based on Makefile rules
dependencies = {
  'b_da_arrays_all.f90': ['a_scratch_size.f90'],
  'c_dabnew.f90': ['b_da_arrays_all.f90'],
  'd_lielib.f90': ['c_dabnew.f90'],
  'h_definition.f90': ['d_lielib.f90'],
  'i_tpsa.f90': ['h_definition.f90'],
  'j_tpsalie.f90': ['i_tpsa.f90'],
  'k_tpsalie_analysis.f90': ['j_tpsalie.f90'],
  'l_complex_taylor.f90': ['k_tpsalie_analysis.f90'],
  'm_real_polymorph.f90': ['l_complex_taylor.f90'],
  'n_complex_polymorph.f90': ['m_real_polymorph.f90'],
  'o_tree_element.f90': ['n_complex_polymorph.f90'],
  'Sa_extend_poly.f90': ['o_tree_element.f90'],
  'Sb_sagan_pol_arbitrary.f90': ['Sa_extend_poly.f90'],
  'Sc_euclidean.f90': ['Sb_sagan_pol_arbitrary.f90'],
  'Sd_frame.f90': ['Sc_euclidean.f90'],
  'Se_status.f90': ['Sd_frame.f90'],
  'Sf_def_all_kinds.f90': ['Se_status.f90'],
  'Sg_sagan_wiggler.f90': ['Sf_def_all_kinds.f90'],
  'Sh_def_kind.f90': ['Sg_sagan_wiggler.f90'],
  'Si_def_element.f90': ['Sh_def_kind.f90'],
  'Sk_link_list.f90': ['Si_def_element.f90'],
  'Sl_family.f90': ['Sk_link_list.f90'],
  'Sm_tracking.f90': ['Sl_family.f90'],
  'Sma0_beam_beam_ptc.f90': ['Sm_tracking.f90'],
  'Sma_multiparticle.f90': ['Sma0_beam_beam_ptc.f90'],
  'Sn_mad_like.f90': ['Sma_multiparticle.f90'],
  'So_fitting.f90': ['Sn_mad_like.f90'],
  'Sp_keywords.f90': ['So_fitting.f90'],
  'Sq_orbit_ptc.f90': ['Sp_keywords.f90'],
  'Sr_spin.f90': ['Sq_orbit_ptc.f90'],
  'Sra_fitting.f90': ['Sr_spin.f90'],
  'Ss_fake_mad.f90': ['Sra_fitting.f90'],
  'St_pointers.f90': ['Ss_fake_mad.f90'],
  'ptcinterface.f90': ['St_pointers.f90']
}

#~ # Build library with proper ordering
#~ ordered_fort_sources = []
#~ visited = []

#~ foreach src : fort_sources
#~   if dependencies.has(src.basename())
#~     foreach dep : dependencies[src.basename()]
#~       if dep not in visited
#~         ordered_fort_sources += files('source/' + dep)
#~         visited += dep
#~       endif
#~     endforeach
#~   endif
#~   ordered_fort_sources += src
#~ endforeach

# Build shared library
#~ libptc = shared_library(
libptc = library(
  'ptc',
#~   ordered_fort_sources,
  fort_sources,
  include_directories: ptc_inc_dirs,
  cpp_args: ['-fPIC', '-std=c++11'],
  dependencies: [core_dep],  
  install: true
)
