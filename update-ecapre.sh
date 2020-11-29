#!/bin/sh

if [ -z $1 ] ; then
    echo "usage:"
    echo "    update-ecapre.sh   master   [git_repo]"
    echo
    echo "    (i) Default git_repo:                     'Rsantct'"
    echo "        You can use another branch name than  'master' "
    echo
    exit 0
fi
branch=$1

if [ $2 ]; then
    gitsite="https://github.com/""$2"
else
    gitsite="https://github.com/Rsantct"
fi

echo
echo "(i) Will download from: [ ""$gitsite"" ]"
read -r -p "    Is this OK? [y/N] " tmp
if [ "$tmp" != "y" ] && [ "$tmp" != "Y" ]; then
    echo 'Bye.'
    exit 0
fi

cd ~/

# Remove previous
rm -f ~/$branch.zip*                    1>/dev/null 2>&1

# Download project from GitHUb
curl -LO "$gitsite"/ecapre/archive/$branch.zip

# Unzip ( ~/ecapre-master/... )
unzip -o $branch.zip

# Move old to keep user files
rm -rf  ~/ecapre.PREV                   1>/dev/null 2>&1
mv -f   ~/ecapre       ~/ecapre.PREV

# Rename downloaded folder
mv ~/ecapre-$branch ~/ecapre

# Executable flags
chmod +x ~/ecapre/*.py                  1>/dev/null 2>&1
chmod +x ~/ecapre/*.sh                  1>/dev/null 2>&1
chmod +x ~/ecapre/share/*.py            1>/dev/null 2>&1
chmod +x ~/ecapre/share/*.sh            1>/dev/null 2>&1
chmod +x ~/ecapre/share/scripts/*       1>/dev/null 2>&1
chmod +x ~/ecapre/share/services/*      1>/dev/null 2>&1

# Leaving a dummy file with the installes branch name
touch ~/ecapre/THIS_BRANCH_IS_$branch

# Removing .zip
rm -f ~/$branch.zip

# Restoring user files
cp ~/ecapre.PREV/.state.yml      ~/ecapre
cp ~/ecapre.PREV/*.config        ~/ecapre
cp ~/ecapre.PREV/macros/*        ~/ecapre/macros/

echo
echo updated:  "$HOME"/ecapre
echo
