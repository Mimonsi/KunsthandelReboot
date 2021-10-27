rmdir /s/q "dist"
python -m build -w
scp ./dist/*.whl root@h2917178.stratoserver.net:/opt/KunsthandelReboot/