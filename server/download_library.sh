cd app/static
rm -r library
mkdir library
wget https://api.github.com/repos/MaayanLab/biojupies-plugins/zipball/$LIBRARY_VERSION
unzip $LIBRARY_VERSION
mv $(find . -iname 'MaayanLab-biojupies-plugins-*')/library library/$LIBRARY_VERSION
ls library
mkdir /download