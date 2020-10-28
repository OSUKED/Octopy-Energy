call cd ..
call conda activate Octopy-Energy
call python setup.py sdist bdist_wheel
call twine upload --skip-existing dist/*
pause