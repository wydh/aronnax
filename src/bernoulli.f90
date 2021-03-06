module bernoulli
  use boundaries
  implicit none

  contains
  ! ---------------------------------------------------------------------------

  !> Evaluate the Bornoulli Potential for n-layer physics.
  !! B is evaluated at the tracer point, for each grid box.
  subroutine evaluate_b_iso(b, h, u, v, nx, ny, layers, g_vec, depth)
    implicit none

    ! Evaluate the baroclinic component of the Bernoulli Potential
    ! (u dot u + Montgomery potential) in the n-layer physics, at centre
    ! of grid box

    double precision, intent(out) :: b(0:nx+1, 0:ny+1, layers) !< Bernoulli Potential
    double precision, intent(in)  :: h(0:nx+1, 0:ny+1, layers) !< layer thicknesses
    double precision, intent(in)  :: u(0:nx+1, 0:ny+1, layers) !< zonal velocities
    double precision, intent(in)  :: v(0:nx+1, 0:ny+1, layers) !< meridional velocities
    integer, intent(in) :: nx !< number of x grid points
    integer, intent(in) :: ny !< number of y grid points
    integer, intent(in) :: layers !< number of layers
    double precision, intent(in)  :: g_vec(layers) !< reduced gravity at each interface
    double precision, intent(in)  :: depth(0:nx+1, 0:ny+1) !< total depth of fluid

    integer i, j, k
    double precision z(0:nx+1, 0:ny+1, layers)
    double precision M(0:nx+1, 0:ny+1, layers)

    ! Calculate layer interface locations
    z = 0d0
    z(:, :, layers) = -depth

    do k = 1, layers-1
      z(:, :, layers - k) = z(:, :, layers-k+1) + h(:, :, layers-k+1)
    end do

    ! Calculate Montogmery potential
    ! The following loop is to get the baroclinic Montgomery potential
    ! in each layer
    M = 0d0
    do k = 2, layers
      M(:, :, k) = M(:, :, k-1) + g_vec(k) * z(:, :, k-1)
    end do

    b = 0d0
    ! No baroclinic pressure contribution to the first layer Bernoulli
    ! potential (the barotropic pressure contributes, but that's not
    ! done here).
    ! do j = 1, ny-1
    !     do i = 1, nx-1
    !         b(i,j,1) = (u(i,j,1)**2+u(i+1,j,1)**2+v(i,j,1)**2+v(i,j+1,1)**2)/4.0d0
    !     end do
    ! end do

    ! For the rest of the layers we get a baroclinic pressure contribution
    do k = 1, layers ! move through the different layers of the model
      do j = 1, ny ! move through longitude
        do i = 1, nx ! move through latitude
          b(i,j,k) = M(i,j,k) &
              + (u(i,j,k)**2+u(i+1,j,k)**2+v(i,j,k)**2+v(i,j+1,k)**2)/4.0d0
          ! Add the (u^2 + v^2)/2 term to the Montgomery Potential
        end do
      end do
    end do

    call wrap_fields_3D(b, nx, ny, layers)


    return
  end subroutine evaluate_b_iso

  ! ---------------------------------------------------------------------------

  subroutine evaluate_b_RedGrav(b, h, u, v, nx, ny, layers, gr)
    implicit none

    ! Evaluate Bernoulli Potential at centre of grid box
    double precision, intent(out) :: b(0:nx+1, 0:ny+1, layers)
    double precision, intent(in)  :: h(0:nx+1, 0:ny+1, layers)
    double precision, intent(in)  :: u(0:nx+1, 0:ny+1, layers)
    double precision, intent(in)  :: v(0:nx+1, 0:ny+1, layers)
    integer, intent(in) :: nx, ny, layers
    double precision, intent(in)  :: gr(layers)

    integer i, j, k, l, m
    double precision h_temp, b_proto

    b = 0d0

    do k = 1, layers ! move through the different layers of the model
      do j = 1, ny ! move through longitude
        do i = 1, nx ! move through latitude
          ! The following loops are to get the pressure term in the
          ! Bernoulli Potential
          b_proto = 0d0
          do l = k, layers
            h_temp = 0d0
            do m = 1, l
              h_temp = h_temp + h(i, j, m) ! sum up the layer thicknesses
            end do
            ! Sum up the product of reduced gravity and summed layer
            ! thicknesses to form the pressure componenet of the
            ! Bernoulli Potential term
            b_proto = b_proto + gr(l)*h_temp
          end do
          ! Add the (u^2 + v^2)/2 term to the pressure componenet of the
          ! Bernoulli Potential
          b(i,j,k) = b_proto &
              + (u(i,j,k)**2+u(i+1,j,k)**2+v(i,j,k)**2+v(i,j+1,k)**2)/4.0d0
        end do
      end do
    end do

    call wrap_fields_3D(b, nx, ny, layers)

    return
  end subroutine evaluate_b_RedGrav

end module bernoulli
