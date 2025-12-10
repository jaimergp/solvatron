# solvatron

A debugging tool for conda solves.

## Examples

```bash
$ pixi run cli -s pixi -c conda-forge numpy
----------------
Solving for pixi
----------------

✨🌟✨ Solution found!

conda-forge/osx-arm64::_openmp_mutex-4.5-7_kmp_llvm
conda-forge/osx-arm64::bzip2-1.0.8-hd037594_8
conda-forge/noarch::ca-certificates-2025.11.12-hbd8a1cb_0
conda-forge/osx-arm64::libblas-3.11.0-4_h51639a9_openblas
conda-forge/osx-arm64::libcblas-3.11.0-4_hb0561ab_openblas
conda-forge/osx-arm64::libcxx-21.1.7-hf598326_0
conda-forge/osx-arm64::libexpat-2.7.3-haf25636_0
conda-forge/osx-arm64::libffi-3.5.2-he5f378a_0
conda-forge/osx-arm64::libgcc-15.2.0-hcbb3090_16
conda-forge/osx-arm64::libgfortran-15.2.0-h07b0088_16
conda-forge/osx-arm64::libgfortran5-15.2.0-hdae7583_16
conda-forge/osx-arm64::liblapack-3.11.0-4_hd9741b5_openblas
conda-forge/osx-arm64::liblzma-5.8.1-h39f12f2_2
conda-forge/osx-arm64::libmpdec-4.0.0-h5505292_0
conda-forge/osx-arm64::libopenblas-0.3.30-openmp_ha158390_3
conda-forge/osx-arm64::libsqlite-3.51.1-h9a5124b_0
conda-forge/osx-arm64::libzlib-1.3.1-h8359307_2
conda-forge/osx-arm64::llvm-openmp-21.1.7-h4a912ad_0
conda-forge/osx-arm64::ncurses-6.5-h5e97a16_3
conda-forge/osx-arm64::numpy-2.3.5-py314h5b5928d_0
conda-forge/osx-arm64::openssl-3.6.0-h5503f6c_0
conda-forge/osx-arm64::python-3.14.2-h40d2674_100_cp314
conda-forge/noarch::python_abi-3.14-8_cp314
conda-forge/osx-arm64::readline-8.2-h1d1bf99_2
conda-forge/osx-arm64::tk-8.6.13-h892fb3f_3
conda-forge/noarch::tzdata-2025b-h78e105d_0
conda-forge/osx-arm64::zstd-1.5.7-hbf9d68e_6

⏱️ Took 0:00:00.166299s
```

```bash
$ pixi run cli -s pixi -s conda --compare -c conda-forge python
-----------------------
Comparing pixi vs conda
-----------------------

✨🌟✨ Solution found!

conda-forge/osx-arm64::bzip2-1.0.8-hd037594_8
conda-forge/noarch::ca-certificates-2025.11.12-hbd8a1cb_0
conda-forge/osx-arm64::libexpat-2.7.3-haf25636_0
conda-forge/osx-arm64::libffi-3.5.2-he5f378a_0
conda-forge/osx-arm64::liblzma-5.8.1-h39f12f2_2
conda-forge/osx-arm64::libmpdec-4.0.0-h5505292_0
conda-forge/osx-arm64::libsqlite-3.51.1-h9a5124b_0
conda-forge/osx-arm64::libzlib-1.3.1-h8359307_2
conda-forge/osx-arm64::ncurses-6.5-h5e97a16_3
conda-forge/osx-arm64::openssl-3.6.0-h5503f6c_0
conda-forge/osx-arm64::python-3.14.2-h40d2674_100_cp314
conda-forge/noarch::python_abi-3.14-8_cp314
conda-forge/osx-arm64::readline-8.2-h1d1bf99_2
conda-forge/osx-arm64::tk-8.6.13-h892fb3f_3
conda-forge/noarch::tzdata-2025b-h78e105d_0
conda-forge/osx-arm64::zstd-1.5.7-hbf9d68e_6

⏱️  pixi took 0:00:00.148796s
⏱️  conda took 0:00:01.099946s
```

```
$ pixi run cli -s pixi -s conda --compare -c conda-forge openmpi --platform=linux-64
-----------------------
Comparing pixi vs conda
-----------------------

⚠️ Different solutions observed!

Legend:
  same in both
- only in pixi
+ only in conda

Diff:
  conda-forge/linux-64::_libgcc_mutex-0.1-conda_forge
  conda-forge/linux-64::_openmp_mutex-4.5-2_gnu
- conda-forge/linux-64::attr-2.5.2-h39aace5_0
- conda-forge/noarch::ca-certificates-2025.11.12-hbd8a1cb_0
- conda-forge/linux-64::libcap-2.77-h3ff7636_0
- conda-forge/linux-64::libevent-2.1.12-hf998b51_1
- conda-forge/linux-64::libfabric-2.3.1-ha770c72_1
- conda-forge/linux-64::libfabric1-2.3.1-h6c8fc0a_1
- conda-forge/linux-64::libgcc-15.2.0-he0feb66_16
?                               ^      ^^ ^^^^  -

+ conda-forge/linux-64::libgcc-14.2.0-h77fa898_1
?                               ^      ^^ ^^^^

- conda-forge/linux-64::libgcc-ng-15.2.0-h69a702a_16
?                                  ^               -

+ conda-forge/linux-64::libgcc-ng-14.2.0-h69a702a_1
?                                  ^

- conda-forge/linux-64::libgfortran-15.2.0-h69a702a_16
?                                    ^               -

+ conda-forge/linux-64::libgfortran-14.2.0-h69a702a_1
?                                    ^

+ conda-forge/linux-64::libgfortran-ng-14.2.0-h69a702a_1
- conda-forge/linux-64::libgfortran5-15.2.0-h68bc16d_16
?                                     ^       ------  -

+ conda-forge/linux-64::libgfortran5-14.2.0-hd5240d6_1
?                                     ^      ++++++

- conda-forge/linux-64::libgomp-15.2.0-he0feb66_16
?                                ^      ^^ ^^^^  -

+ conda-forge/linux-64::libgomp-14.2.0-h77fa898_1
?                                ^      ^^ ^^^^

- conda-forge/linux-64::libhwloc-2.12.1-default_hafda6a7_1003
- conda-forge/linux-64::libiconv-1.18-h3b78370_2
- conda-forge/linux-64::liblzma-5.8.1-hb9d3cd8_2
- conda-forge/linux-64::libnl-3.11.0-hb9d3cd8_0
- conda-forge/linux-64::libpmix-5.0.8-h4bd6b51_2
- conda-forge/linux-64::libstdcxx-15.2.0-h934c35e_16
?                                  ^      ^ -  ^^  -

+ conda-forge/linux-64::libstdcxx-14.2.0-hc0a3c3a_1
?                                  ^      ^^^   ^

+ conda-forge/linux-64::libstdcxx-ng-14.2.0-h4852527_1
- conda-forge/linux-64::libsystemd0-257.10-hd0affe5_2
- conda-forge/linux-64::libudev1-257.10-hd0affe5_2
- conda-forge/linux-64::libxml2-2.15.1-h031cc0b_0
- conda-forge/linux-64::libxml2-16-2.15.1-hf2a90c1_0
- conda-forge/linux-64::libzlib-1.3.1-hb9d3cd8_2
?                                       ^^^^^  ^

+ conda-forge/linux-64::libzlib-1.3.1-h4ab18f5_1
?                                      ++ ^ ++ ^

- conda-forge/noarch::mpi-1.0.1-openmpi
?              ^^^^^         --

+ conda-forge/linux-64::mpi-1.0-openmpi
?             ++ ^^^^^

- conda-forge/linux-64::openmpi-5.0.8-h2fe1745_109
?                               ^ ^ ^    -----   ^

+ conda-forge/linux-64::openmpi-4.1.6-hc5af2df_101
?                               ^ ^ ^  ++++ +    ^

- conda-forge/linux-64::openssl-3.6.0-h26f9b46_0
- conda-forge/linux-64::rdma-core-60.0-hecca717_0
- conda-forge/linux-64::ucc-1.6.0-hb729f83_1
?                       ^^^   ^ ^   ^^^ ^^

+ conda-forge/linux-64::zlib-1.3.1-h4ab18f5_1
?                       ^^^^   ^ ^  ++ ^^ ^

- conda-forge/linux-64::ucx-1.19.1-h567e125_0
```
