module pyptc_api_module
  use iso_c_binding, only: c_char, c_double, c_int, c_null_char
  use pointer_lattice
  use orbit_ptc
  use ptc_multiparticle, only: x_orbit_sync
  use S_fitting, only: lattice_GET_tune, lattice_GET_CHROM, assign_one_aperture, TURN_OFF_ONE_aperture
  use S_FAMILY, only: MISALIGN_FIBRE, MAD_MISALIGN_FIBRE
  implicit none

contains
  logical function pyptc_ready()
    if (.not. associated(my_ering) .or. .not. associated(my_estate)) then
      call set_lattice_pointers()
    end if
    pyptc_ready = associated(my_ering) .and. associated(my_estate)
  end function pyptc_ready

  logical function pyptc_valid_pos(pos)
    integer(c_int), value, intent(in) :: pos
    pyptc_valid_pos = pyptc_ready() .and. pos >= 1_c_int .and. pos <= my_ering%n
  end function pyptc_valid_pos

  subroutine pyptc_copy_c_string(c_string, f_string, status)
    character(kind=c_char), intent(in) :: c_string(*)
    character(len=*), intent(out) :: f_string
    integer(c_int), intent(out) :: status
    integer :: i

    f_string = ' '
    status = 0_c_int
    do i = 1, len(f_string)
      if (c_string(i) == c_null_char) return
      f_string(i:i) = c_string(i)
    end do
    status = 2_c_int
  end subroutine pyptc_copy_c_string

  subroutine pyptc_get_api_level(api_level) bind(C, name="pyptc_get_api_level")
    integer(c_int), intent(out) :: api_level
    api_level = 2_c_int
  end subroutine pyptc_get_api_level

  subroutine pyptc_get_tunes(qx, qy, qs, status) bind(C, name="pyptc_get_tunes")
    real(c_double), intent(out) :: qx, qy, qs
    integer(c_int), intent(out) :: status
    integer :: mf, ios
    real(c_double) :: t0
    type(internal_state) :: state

    qx = 0.0_c_double
    qy = 0.0_c_double
    qs = 0.0_c_double
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if

    state = ((((my_estate + nocavity0) - delta0) + only_4d0) - RADIATION0)
    open(newunit=mf, status='scratch', action='readwrite')
    call lattice_GET_tune(my_ering, state, mf)
    rewind(mf)
    read(mf, *, iostat=ios) t0, qx, qy, qs
    if (ios /= 0) then
      rewind(mf)
      read(mf, *, iostat=ios) t0, qx, qy
      qs = 0.0_c_double
    end if
    close(mf)
    if (ios /= 0) status = 3_c_int
    if (.not. check_stable) status = 4_c_int
  end subroutine pyptc_get_tunes

  subroutine pyptc_get_chromaticities(chromx, chromy, status) bind(C, name="pyptc_get_chromaticities")
    real(c_double), intent(out) :: chromx, chromy
    integer(c_int), intent(out) :: status
    real(c_double) :: chrom(2)

    chromx = 0.0_c_double
    chromy = 0.0_c_double
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if

    chrom = 0.0_c_double
    call lattice_GET_CHROM(my_ering, my_estate, chrom)
    chromx = chrom(1)
    chromy = chrom(2)
    if (.not. check_stable) status = 4_c_int
  end subroutine pyptc_get_chromaticities

  subroutine pyptc_set_misalignment(pos, mis, status) bind(C, name="pyptc_set_misalignment")
    integer(c_int), value, intent(in) :: pos
    real(c_double), intent(in) :: mis(6)
    integer(c_int), intent(out) :: status
    type(fibre), pointer :: p
    real(dp) :: local_mis(6)

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if

    call move_to(my_ering, p, int(pos))
    local_mis = real(mis, dp)
    call MISALIGN_FIBRE(p, local_mis)
  end subroutine pyptc_set_misalignment

  subroutine pyptc_set_madx_misalignment(pos, mis, status) bind(C, name="pyptc_set_madx_misalignment")
    integer(c_int), value, intent(in) :: pos
    real(c_double), intent(in) :: mis(6)
    integer(c_int), intent(out) :: status
    type(fibre), pointer :: p
    real(dp) :: local_mis(6)

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if

    call move_to(my_ering, p, int(pos))
    local_mis = real(mis, dp)
    call MAD_MISALIGN_FIBRE(p, local_mis)
  end subroutine pyptc_set_madx_misalignment

  subroutine pyptc_set_one_aperture(pos, kindaper, r, x, y, dx, dy, status) bind(C, name="pyptc_set_one_aperture")
    integer(c_int), value, intent(in) :: pos, kindaper
    real(c_double), intent(in) :: r(2)
    real(c_double), value, intent(in) :: x, y, dx, dy
    integer(c_int), intent(out) :: status
    real(dp) :: local_r(2)

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if

    local_r = real(r, dp)
    call assign_one_aperture(my_ering, int(pos), int(kindaper), local_r, real(x, dp), real(y, dp), real(dx, dp), real(dy, dp))
  end subroutine pyptc_set_one_aperture

  subroutine pyptc_turn_off_one_aperture(pos, status) bind(C, name="pyptc_turn_off_one_aperture")
    integer(c_int), value, intent(in) :: pos
    integer(c_int), intent(out) :: status

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if

    call TURN_OFF_ONE_aperture(my_ering, int(pos))
  end subroutine pyptc_turn_off_one_aperture

  subroutine pyptc_set_absolute_aperture(value, status) bind(C, name="pyptc_set_absolute_aperture")
    real(c_double), value, intent(in) :: value
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (value <= 0.0_c_double) then
      status = 2_c_int
      return
    end if
    absolute_aperture = real(value, dp)
  end subroutine pyptc_set_absolute_aperture

  subroutine pyptc_get_absolute_aperture(value) bind(C, name="pyptc_get_absolute_aperture")
    real(c_double), intent(out) :: value
    value = real(absolute_aperture, c_double)
  end subroutine pyptc_get_absolute_aperture

  subroutine pyptc_track_particle_ring_loss(x, nturn, lost, lost_turn, lost_pos, status) bind(C, name="pyptc_track_particle_ring_loss")
    real(c_double), intent(inout) :: x(6)
    integer(c_int), value, intent(in) :: nturn
    integer(c_int), intent(out) :: lost, lost_turn, lost_pos, status
    integer :: i, turn

    lost = 0_c_int
    lost_turn = 0_c_int
    lost_pos = 0_c_int
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    if (nturn < 1_c_int) then
      status = 2_c_int
      return
    end if

    call RESET_APERTURE_FLAG()
    if (abs(x(1)) + abs(x(3)) > absolute_aperture) then
      lost = 1_c_int
      lost_turn = 1_c_int
      lost_pos = 1_c_int
      return
    end if
    do turn = 1, int(nturn)
      do i = 0, my_ORBIT_LATTICE%ORBIT_N_NODE - 1
        call PUT_RAY(x(1), x(2), x(3), x(4), x(5), x(6))
        call TRACK_ONE_NODE(i + 1)
        call GET_RAY(x(1), x(2), x(3), x(4), x(5), x(6))
        if (abs(x(1)) + abs(x(3)) > absolute_aperture) then
          lost = 1_c_int
          lost_turn = int(turn, c_int)
          lost_pos = int(i + 1, c_int)
          call RESET_APERTURE_FLAG()
          return
        end if
        if (.not. check_stable) then
          lost = 1_c_int
          lost_turn = int(turn, c_int)
          lost_pos = int(i + 1, c_int)
          call RESET_APERTURE_FLAG()
          return
        end if
      end do
    end do
  end subroutine pyptc_track_particle_ring_loss

  subroutine pyptc_set_acceleration(flag, status) bind(C, name="pyptc_set_acceleration")
    integer(c_int), value, intent(in) :: flag
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    accelerate = flag /= 0_c_int
  end subroutine pyptc_set_acceleration

  subroutine pyptc_set_ramping(flag, status) bind(C, name="pyptc_set_ramping")
    integer(c_int), value, intent(in) :: flag
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    RAMP = flag /= 0_c_int
  end subroutine pyptc_set_ramping

  subroutine pyptc_set_modulation(flag, status) bind(C, name="pyptc_set_modulation")
    integer(c_int), value, intent(in) :: flag
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    if (flag /= 0_c_int) then
      my_estate = my_estate + MODULATION0
    else
      my_estate = my_estate - MODULATION0
    end if
  end subroutine pyptc_set_modulation

  subroutine pyptc_set_cavity(flag, status) bind(C, name="pyptc_set_cavity")
    integer(c_int), value, intent(in) :: flag
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    if (flag /= 0_c_int) then
      my_estate = my_estate - NOCAVITY0
    else
      my_estate = my_estate + NOCAVITY0
    end if
  end subroutine pyptc_set_cavity

  subroutine pyptc_store_orbit_state(status) bind(C, name="pyptc_store_orbit_state")
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    my_ORBIT_LATTICE%state = my_estate
  end subroutine pyptc_store_orbit_state

  subroutine pyptc_use_orbit_state(status) bind(C, name="pyptc_use_orbit_state")
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    my_estate = my_ORBIT_LATTICE%state
  end subroutine pyptc_use_orbit_state

  subroutine pyptc_set_all_ramp(status) bind(C, name="pyptc_set_all_ramp")
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    call set_all_ramp(my_ering)
  end subroutine pyptc_set_all_ramp

  subroutine pyptc_energize_lattice(t, use_t, status) bind(C, name="pyptc_energize_lattice")
    real(c_double), value, intent(in) :: t
    integer(c_int), value, intent(in) :: use_t
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    if (use_t /= 0_c_int) then
      call energize_ORBIT_lattice(real(t, dp))
    else
      call energize_ORBIT_lattice()
    end if
  end subroutine pyptc_energize_lattice

  subroutine pyptc_set_orbit_time(t, status) bind(C, name="pyptc_set_orbit_time")
    real(c_double), value, intent(in) :: t
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    x_orbit_sync = 0.0_dp
    x_orbit_sync(6) = real(t, dp)
    xsm0%ac%t = real(t, dp)
  end subroutine pyptc_set_orbit_time

  subroutine pyptc_initialize_cavity(pos, c_filename, status) bind(C, name="pyptc_initialize_cavity")
    integer(c_int), value, intent(in) :: pos
    character(kind=c_char), intent(in) :: c_filename(*)
    integer(c_int), intent(out) :: status
    character(len=512) :: filename
    integer(c_int) :: string_status
    type(fibre), pointer :: p

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if
    call pyptc_copy_c_string(c_filename, filename, string_status)
    if (string_status /= 0_c_int) then
      status = string_status
      return
    end if
    call move_to(my_ering, p, int(pos))
    call lecture_fichier(p%mag, trim(filename))
  end subroutine pyptc_initialize_cavity

  subroutine pyptc_close_cavity_ring(status) bind(C, name="pyptc_close_cavity_ring")
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. associated(paccfirst) .or. .not. associated(paccthen)) then
      status = 1_c_int
      return
    end if
    paccthen%mag%c4%acc%next => paccfirst
    paccfirst%mag%c4%acc%previous => paccthen
  end subroutine pyptc_close_cavity_ring

  subroutine pyptc_power_cavity(harmonic_number, volt, phase, epsf, status) bind(C, name="pyptc_power_cavity")
    integer(c_int), value, intent(in) :: harmonic_number
    real(c_double), value, intent(in) :: volt, phase, epsf
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    call power_cavity(my_ering, int(harmonic_number), real(volt, dp), real(phase, dp), real(epsf, dp))
  end subroutine pyptc_power_cavity

  subroutine pyptc_cavity_totalpath(pos, status) bind(C, name="pyptc_cavity_totalpath")
    integer(c_int), value, intent(in) :: pos
    integer(c_int), intent(out) :: status
    status = 0_c_int
    if (.not. pyptc_ready()) then
      status = 1_c_int
      return
    end if
    if (pos /= 0_c_int .and. pos /= 1_c_int) then
      status = 2_c_int
      return
    end if
    call totalpath_cavity(my_ering, int(pos))
  end subroutine pyptc_cavity_totalpath

  subroutine pyptc_configure_ac_magnet(pos, dc, amp, phase_turns, d_ac, n, bn, an, status) bind(C, name="pyptc_configure_ac_magnet")
    integer(c_int), value, intent(in) :: pos, n
    real(c_double), value, intent(in) :: dc, amp, phase_turns, d_ac
    real(c_double), intent(in) :: bn(*), an(*)
    integer(c_int), intent(out) :: status
    integer :: i, nmul
    type(fibre), pointer :: p

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if
    if (n < 0_c_int) then
      status = 2_c_int
      return
    end if

    call move_to(my_ering, p, int(pos))
    if (associated(p%mag%DC_ac)) then
      status = 3_c_int
      return
    end if

    allocate(p%mag%DC_ac)
    allocate(p%mag%A_ac)
    allocate(p%mag%theta_ac)
    allocate(p%mag%D_ac)
    allocate(p%magp%DC_ac)
    allocate(p%magp%A_ac)
    allocate(p%magp%theta_ac)
    call alloc(p%magp%DC_ac)
    call alloc(p%magp%A_ac)
    call alloc(p%magp%theta_ac)
    allocate(p%magp%D_ac)
    call alloc(p%magp%D_ac)

    p%mag%D_ac = real(d_ac, dp)
    p%mag%DC_ac = real(dc, dp)
    p%mag%A_ac = real(amp, dp)
    p%mag%theta_ac = real(phase_turns, dp) * twopi
    p%magp%D_ac = real(d_ac, dp)
    p%magp%DC_ac = real(dc, dp)
    p%magp%A_ac = real(amp, dp)
    p%magp%theta_ac = real(phase_turns, dp) * twopi
    p%mag%slow_ac = .true.
    p%magp%slow_ac = .true.

    if (n > p%mag%p%nmul) call ADD(p, int(n), 0, 0.0_dp)
    nmul = p%mag%p%nmul
    allocate(p%mag%d_an(nmul))
    allocate(p%mag%d_bn(nmul))
    allocate(p%magp%d_an(nmul))
    allocate(p%magp%d_bn(nmul))
    allocate(p%mag%d0_an(nmul))
    allocate(p%mag%d0_bn(nmul))
    allocate(p%magp%d0_an(nmul))
    allocate(p%magp%d0_bn(nmul))
    p%mag%d_an = 0.0_dp
    p%mag%d_bn = 0.0_dp
    call alloc(p%magp%d_an, nmul)
    call alloc(p%magp%d_bn, nmul)
    call alloc(p%magp%d0_an, nmul)
    call alloc(p%magp%d0_bn, nmul)

    do i = 1, nmul
      p%mag%d0_bn(i) = p%mag%bn(i)
      p%mag%d0_an(i) = p%mag%an(i)
      p%magp%d0_bn(i) = p%mag%bn(i)
      p%magp%d0_an(i) = p%mag%an(i)
    end do
    do i = 1, min(int(n), nmul)
      p%mag%d_bn(i) = real(bn(i), dp)
      p%magp%d_bn(i) = real(bn(i), dp)
      p%mag%d_an(i) = real(an(i), dp)
      p%magp%d_an(i) = real(an(i), dp)
    end do
  end subroutine pyptc_configure_ac_magnet

  subroutine pyptc_configure_ramp_magnet(pos, c_filename, hgap, status) bind(C, name="pyptc_configure_ramp_magnet")
    integer(c_int), value, intent(in) :: pos
    character(kind=c_char), intent(in) :: c_filename(*)
    real(c_double), value, intent(in) :: hgap
    integer(c_int), intent(out) :: status
    character(len=512) :: filename
    integer(c_int) :: string_status
    integer :: i, nmul, table_nmul
    type(fibre), pointer :: p

    status = 0_c_int
    if (.not. pyptc_valid_pos(pos)) then
      status = 1_c_int
      return
    end if
    call pyptc_copy_c_string(c_filename, filename, string_status)
    if (string_status /= 0_c_int) then
      status = string_status
      return
    end if

    call move_to(my_ering, p, int(pos))
    if (associated(p%mag%DC_ac)) then
      status = 3_c_int
      return
    end if

    call reading_file(p%mag, trim(filename))
    p%mag%ramp%r = real(hgap, dp)
    p%magp%ramp%r = real(hgap, dp)
    table_nmul = size(p%mag%ramp%table(0)%bn)

    allocate(p%mag%DC_ac)
    allocate(p%mag%A_ac)
    allocate(p%mag%theta_ac)
    allocate(p%mag%D_ac)
    allocate(p%magp%DC_ac)
    allocate(p%magp%A_ac)
    allocate(p%magp%theta_ac)
    call alloc(p%magp%DC_ac)
    call alloc(p%magp%A_ac)
    call alloc(p%magp%theta_ac)
    allocate(p%magp%D_ac)
    call alloc(p%magp%D_ac)

    p%mag%D_ac = 0.0_dp
    p%mag%DC_ac = 1.0_dp
    p%mag%A_ac = 0.0_dp
    p%mag%theta_ac = 0.0_dp
    p%magp%D_ac = 0.0_dp
    p%magp%DC_ac = 1.0_dp
    p%magp%A_ac = 0.0_dp
    p%magp%theta_ac = 0.0_dp
    p%mag%slow_ac = .true.
    p%magp%slow_ac = .true.

    if (table_nmul > p%mag%p%nmul) call ADD(p, table_nmul, 0, 0.0_dp)
    nmul = p%mag%p%nmul
    allocate(p%mag%d_an(nmul))
    allocate(p%mag%d_bn(nmul))
    allocate(p%magp%d_an(nmul))
    allocate(p%magp%d_bn(nmul))
    allocate(p%mag%d0_an(nmul))
    allocate(p%mag%d0_bn(nmul))
    allocate(p%magp%d0_an(nmul))
    allocate(p%magp%d0_bn(nmul))
    p%mag%d_an = 0.0_dp
    p%mag%d_bn = 0.0_dp
    call alloc(p%magp%d_an, nmul)
    call alloc(p%magp%d_bn, nmul)
    call alloc(p%magp%d0_an, nmul)
    call alloc(p%magp%d0_bn, nmul)
    do i = 1, nmul
      p%mag%d0_bn(i) = p%mag%bn(i)
      p%mag%d0_an(i) = p%mag%an(i)
      p%magp%d0_bn(i) = p%mag%bn(i)
      p%magp%d0_an(i) = p%mag%an(i)
    end do
  end subroutine pyptc_configure_ramp_magnet
end module pyptc_api_module
