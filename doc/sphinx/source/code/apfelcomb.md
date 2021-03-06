## APFELcomb

APFELcomb is the project that allows the user to generate ``FK`` tables. These
are lookup tables that contain the relevant information to compute theoretical 
predicitons in the NNPDF framework. Broadly speaking, this is achieved by 
taking DGLAP evolution kernels from ``APFEL`` and combining them with
interpolated parton-level observable kernels of various forms. The mechanism
behind APFELcomb is presented in [arXiv:1605.02070]().

APFELcomb is available from 
```
https://github.com/NNPDF/apfelcomb
````
The various data formats used in APFELcomb are described in 
```
nnpdf/nnpdfcpp/data/doc/data_layout.pdf
```

APFELcomb depends on the following libraries
* [APFEL](github.com/scarrazza/apfel.git)
* [nnpdf](github.com/NNPDF/nnpdf)
* [APPLgrid](github.com/NNPDF/external/applgrid-1.4.70-nnpd)

and data files from

* [applgrids](github.com/NNPDF/applgrids)

There are various ways of generating the latter, as explained in [How to 
generate applgrids](../tutorials/APPLgrids.md).

Once the above libraries and data files are set up, the APFELcomb project can be
compield as follows
```
make 
```
Compilation flags and various paths are defined in `Makefile.inc`. These are
mostly inferred from `<package>-config` files with the exception of
* `RESULTS_PATH` (default `./results`) Defines the path results are written to.
* `APPL_PATH` (default `../applgrids`) Defines the path to the `applgrid` repository.
* `DB_PATH` (default `.db`) Defines the path to the APFELcomb database.

The defaults are configured assuming that both the `nnpdf` and `applgrid` 
repositories are located at `../`.

Each `FK` table is generated piecewise in one or more `subgrids`. The `subgrids`
implemented in APFELcomb can be displayed by running the script
```
./scripts/disp_grids.py
```
Typically DIS and `FKGenerator` DY tables are made of only one subgrid, whereas
FK tables generated from APPLgrids have one subgrid per APPLgrid file. 
How subgrids are merged into grids, and the generation parameters of each 
subgrid, is specified in the `db/apfelcomb.db` database. The database itself 
is not stored in the repository, but it is built from the sqlite dump at 
`db/apfelcomb.dat`. This is done automatically by the APFELcomb makefile.
Detailed instructions to generate/implement `FK` tables for individual 
experiments and/or a compelte theory are provided in 
[How to generate/implement FK tables](../tutorials/apfelcomb.md).
