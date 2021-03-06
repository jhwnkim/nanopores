%function sgmga_point_tests ( )

%****************************************************************************80
%
%% SGMGA_POINT_TESTS calls SGMGA_POINT_TEST with various arguments.
%
%  Licensing:
%
%    This code is distributed under the GNU LGPL license.
%
%  Modified:
%
%    20 June 2010
%
%  Author:
%
%    John Burkardt
%
%  Local Parameters:
%
%    Local, real TOL, a tolerance for point equality.
%    A value of sqrt ( eps ) is reasonable, and will allow the code to
%    consolidate points which are equal, or very nearly so.  A value of
%    -1.0, on the other hand, will force the code to use every point, regardless
%    of duplication.
%
  addpath ( '../sandia_rules' );

  timestamp ( );

  fprintf ( 1, '\n' );
  fprintf ( 1, 'SGMGA_POINT_TESTS\n' );
  fprintf ( 1, '  Call SGMGA_POINT_TEST with various arguments.\n' );
%
%  Set the point equality tolerance.
%
  tol = sqrt ( eps );
  fprintf ( 1, '\n' );
  fprintf ( 1, '  All tests will use a point equality tolerance of %e\n', tol );

  clc
  %close all
  dim_num = 2;
  importance = zeros(dim_num,1); itest = [1;1];
  for dim = 1 : dim_num
    importance(dim,1) = itest(dim);
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 2;
  level_max_max = 2;
  rule = [ 1, 1 ]'; % 1 = CC, 3 = GP, 4 = GL
  growth = [ 6, 6 ]'; % 6 = FE, 4 = SE, 5 = ME
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );
%%{
  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 1 ]';
  growth = [ 6, 6 ]';
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 3;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = 1.0;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 1, 1 ]';
  growth = [ 6, 6, 6 ]';
  np = [ 0, 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 3;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 1, 1 ]';
  growth = [ 6, 6, 6 ]';
  np = [ 0, 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 3 ]';
  growth = [ 6, 6 ]';
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 4 ]';
  growth = [ 6, 3 ]';
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 7 ]';
  growth = [ 6, 3 ]';
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 8 ]';
  growth = [ 6, 3 ]';
  np = [ 0, 1 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  p(1) = 1.5;
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 2, 9 ]';
  growth = [ 6, 3 ]';
  np = [ 0, 2 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  p(1,1) = 0.5;
  p(2,1) = 1.5;
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 6, 10 ]';
  growth = [ 3, 4 ]';
  np = [ 1, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  p(1,1) = 2.0;
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );

  dim_num = 3;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 2;
  rule = [ 1, 4, 5 ]';
  growth = [ 6, 3, 3 ]';
  np = [ 0, 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );
%
%  Look at a case of interest to Mike.
%
  dim_num = 2;
  importance = zeros(dim_num,1);
  for dim = 1 : dim_num
    importance(dim,1) = dim_num + 1 - dim;
  end
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 5;
  rule = [ 5, 5 ]';
  growth = [ 3, 3 ]';
  np = [ 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );
%
%  Look at a case that includes a "0" importance dimension.
%
  dim_num = 3;
  importance = [ 1.0, 0.0, 1.0 ]';
  level_weight = sgmga_importance_to_aniso ( dim_num, importance );
  level_max_min = 0;
  level_max_max = 3;
  rule = [ 1, 1, 1 ]';
  growth = [ 6, 6, 6 ]';
  np = [ 0, 0, 0 ]';
  np_sum = sum ( np(1:dim_num) );
  p = zeros(np_sum,1);
  sgmga_point_test ( dim_num, importance, level_weight, level_max_min, ...
    level_max_max, rule, growth, np, p, tol );
%
%  Terminate.
%
  fprintf ( 1, '\n' );
  fprintf ( 1, 'SGMGA_POINT_TESTS:\n' );
  fprintf ( 1, '  Normal end of execution.\n' );

  fprintf ( 1, '\n' );
  timestamp ( );

  rmpath ( '../sandia_rules' );

  return
end
%}