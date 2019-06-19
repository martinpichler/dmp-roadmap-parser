## DMP-Roadmap setup
While *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap/wiki/Installation)* has an installation guide, the instructions are very outdated, software versions used are sometimes unclear and the general description of the instructions is very short and unprecise. We created our own instructions so that setting up *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap)* is just copy pasting underneath instructions.

*The project was developed and tested on Ubuntu 18.04 64Bit.*

**install nodejs, yarn and other utilities needed to run a ruby on rails application using webpack**

There was no clear definition on which version of nodejs was used. Aftersome troubleshooting we found the software to be working with nodejs version 8.x

```bash
# add the correct repositories
sudo apt install -y curl
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

# install nodejs, yarn and other utilities
sudo apt-get update
sudo apt-get install -y git-core zlib1g-dev build-essential libssl-dev libreadline-dev libyaml-dev libsqlite3-dev sqlite3 libxml2-dev libxslt1-dev libcurl4-openssl-dev software-properties-common libffi-dev nodejs yarn
```

**install git**
```bash
sudo apt-get install git

# check version
git --version
```

**install ruby using *rbenv***
rbenv is a command line tool that lets you mangae and switch between diffrent ruby installations

As in the *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap/wiki/Installation)* installation guide described we use ruby >= 2.4.4
```bash
# clone rbenv and add it to the PATH
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(rbenv init -)"' >> ~/.bashrc
exec $SHELL

git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
echo 'export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"' >> ~/.bashrc
exec $SHELL

# install ruby 2.4.6
rbenv install 2.4.6

# set it as the global (system wide) ruby version
rbenv global 2.4.6

# check version
ruby --version
```

**install rails**
Again we use the recommended version as suggested by *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap/wiki/Installation)* which is rails >= 4.2.10
```bash
# use ruby-gem to install rails
gem install rails -v 4.2.11.1
rbenv rehash

# check version
rails --version
```

As of now we should be able to run ruby on rails applications like *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap)* that use webpacker. We still have to install and configure a database for *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap)* to use. In our case this will be postreSQL.

**install and configure postgreSQL**
Just to make sure we dont run into compatibilitie issues we decided to use version 10 (9.6 is apparently used by dmp-roadmap as there installation guideline linsk to the 9.6 documentation).
```bash
# install postgresql
sudo apt install -y postgresql-10 libpq-dev

# create a user where <name> should be your current user
sudo -u postgres createuser <name> -s

# set a password for the user
sudo -u postgres psql
\password <name>

# create a database for dmp-roadmap
createdb roadmapdb
```
**clone *dmp-roadmap* repository**
```bash
# install dmp-roadmap
git clone https://github.com/DMPRoadmap/roadmap.git
```

**make changes to the dmp-roadmap configuration**
Go to the directory where you cloned *dmp-roadmap* (default is your user directory) and open the *roadmap* folder. Next do the following:
* open *Gemfile* with a text editor and delete following lines:
  ```
  group :mysql do
    # A simple, fast Mysql library for Ruby, binding to libmysql (http://github.com/brianmario/mysql2)
    # A simple, fast Mysql library for Ruby, binding to libmysql (https://github.com/brianmario/mysql2)
    gem 'mysql2', '~> 0.4.10'
  end
  ```
  If you want to use *mysql* instead of *postgreSQL* keep the *mysql* part and delete following lines (you have to install mysql, create a user and a database):
  ```
  group :pgsql do
    # Pg is the Ruby interface to the {PostgreSQL
    # RDBMS}[http://www.postgresql.org/](https://bitbucket.org/ged/ruby-pg)
    # Pg is the Ruby interface to the {PostgreSQL RDBMS}[http://www.postgresql.org/] (https://bitbucket.org/ged/ruby-pg)
    gem 'pg', '~> 0.19.0'
  end
  ```
* open *config/database.yml.sample*. Change the dbname to the name of the database created above. The file should now look like this:
  ```yml
  defaults: &defaults
    adapter: <%= ENV['DB_ADAPTER'] || 'postgresql' %>
    encoding: <%= ENV['DB_ADAPTER'] == "mysql2" ? "utf8mb4" : "" %>
    username: <%= ENV["DB_ADAPTER"] == "postgresql" ? 'postgres' : '' %>
    database: roadmapdb
    pool: 5
  
  development:
    <<: *defaults
  
  test:
    <<: *defaults
  ```

**create config file, seed database and build with webpack**
In the terminal window go to the *roadmap* folder and execute following commands:
```bash
# creates the config files
bin/setup

# make sure all ruby gems are installed
bundle install

# create and seed database
rake db:drop # might show an error/warning which can be ignored
rake db:create
rake db:schema:load
rake db:seed

# build js with webpack
rake webpacker:yarn_install

# start the ruby on rails server
rails s

# if you setup dmp-roadmap in a VM start the server with:
# rails s --binding=0.0.0.0
# this allows access to the server from ip addresses which are not localhost
# be aware that you also have to change the network settings of your VM accordingly
```

CONGRATULATIONS, you now have a running *dmp-roadmap* instance!

## Creating Templates
The default login for a new *dmp-roadmap* instance is:
* super_admin@example.com:password123

We propose the following way to create new templates:
1. Login as Admin
2. In the second level navigation bar open the dropdown menu on the right that says "Admin" and go to "Organisations"
3. Create a new organisation e.g. "My Awesome Research Institute" and just to make sure you can use your templates later, check all of these three options:
   *  Funder
   * Institution
   * Organisation
4. Now in the same "Admin" menu go to "Templates". At the top you find a text input field. Search for your newly created organisation and click on "Change Affiliation"
5. Click on "Create a template" and edit your template to your liking
6. After you are done with your template make sure to switch to the TAB with your organisations name and under the "Actions" dropdown select publish to make your template appear when creating a new DMP.
7. Go to your dashboard and create a new DMP with your organisation as funder and you should have a new DMP with your own template.