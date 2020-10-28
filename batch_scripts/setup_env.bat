call cd ..
call conda env create -f environment.yml
call conda activate Octopy-Energy
call ipython kernel install --user --name=Octopy-Energy
pause