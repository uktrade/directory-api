wget -q https://cli-assets.heroku.com/heroku-linux-x64.tar.gz -O heroku.tar.gz
tar -xzf heroku.tar.gz
mkdir -p ~/bin/heroku-cli
tar -xzf heroku.tar.gz --strip-components 1 -C ~/bin/heroku-cli
rm -fr heroku.tar.gz
ln -s ~/bin/heroku-cli/bin/heroku ~/bin/heroku
export PATH=$PATH:$HOME/bin
heroku -v
cat >~/.netrc <<EOF
machine api.heroku.com
  login $HEROKU_EMAIL
  password $HEROKU_API_KEY
machine git.heroku.com
  login $HEROKU_EMAIL
  password $HEROKU_API_KEY
EOF
chmod 600 ~/.netrc # Heroku cli complains about permissions without this
