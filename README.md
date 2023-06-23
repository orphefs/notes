# notes
Some useful scripting / linux  / coding tricks I've collected along the way

# Git tricks
#### Renaming a git branch
Here are the steps to rename the branch:

1. switch to branch which needs to be renamed
2. git branch -m <new_name>
3. git push origin :<old_name>
4. git push origin <new_name>:refs/heads/<new_name>

#### Deleting a git branch remotely and locally:
    git push origin --delete <branch_name>
    git branch -d <branch_name>
    
#### Displaying files changed by a user since date:

    git log --since="2018-01-31" --author="Mr. Squibbles" --stat --name-only --oneline


# Python tricks

- Running a python script in sudo while preserving environment variables
    ~~~~ 
    sudo -HE env PATH=$PATH PYTHONPATH=$PYTHONPATH python setup.py install
    ~~~~ 

- Using memory profiler to profile python code
    ~~~~ 
    pip install memory-profiler
    ~~~~ 
    Prepend functions to be profiled iwth `@profile`, then run 
    code using 
    ~~~~
    python -m memory_profiler code.py
    ~~~~
    
- Importing functions from a module into a list:
    ~~~~
    check_functions = [func for name, func in inspect.getmembers(checks_module, inspect.isfunction)]
    ~~~~
    

# Networking tricks
- Bringing a network interface down to change its configuration:
    ~~~~
    sudo ifconfig enp12s0 down
    sudo ifconfig enp12s0 10.10.1.2 netmask 255.255.255.0 up
    ~~~~
$ Linux administration tricks

- Forcing package installation if `sudo apt-get install -f` fails:
    ~~~~
    sudo dpkg -i --force-overwrite path-to-the-deb-file
    ~~~~
  



# Bash tricks
- Matching a .json file for a key, then selecting the value (in this case it is a directory) and removing the quotes, and using it with xargs to copy that directory into a `output` directory:
    ~~~~
    cat folders.json | grep my_key | awk '{print $2}' | tr -d '",' | xargs -t -I % bash -c 'cp -r % output/'
    ~~~~


- Using the output of a command as input to another one
    ~~~~ 
    cat `ls | grep .confusionmatrix`
    ~~~~ 
- Passing variable arguments to function 
    ~~~~ 
    function trash() { mv $@ ~/.Trash; }
    ~~~~ 
- Watch the contents of a directory change:
    ~~~~ 
    watch -d ls -l
    ~~~~ 
- Prepend # at beggining of file (in-place modification)
    ~~~~
    sed -i '0,/^[^#]/ s//#&/' file
    ~~~~
- Selectively copy files from server (warning: excludes subdirs due to `--exclude='*'`):
    ~~~~
    rsync -Rv -e ssh --include '*.json' --include '*.txt' --exclude='*' user@server:/path/to/data/ .
    ~~~~
    ~~~~
    rsync -rv -e ssh --include="*.one" --include="*.two" --include="*.three" --include="*/" --exclude="*" --progress             user@server:/path/to/data/*  /path/to/local/
    ~~~~

- Resume a broken scp transfer:
    ~~~~
    rsync --rsh='ssh' -av --progress --partial  user@domain.com:/path/to/data/ .
    ~~~~git reset HEAD~
- Check size of directory:
    ~~~~
    du -h <your_directory>
    ~~~~
- Check the size of directories (sorted)
    ~~~~ 
    du -sh * | sort -h
    ~~~~ 
    
- Use contents of a file as keywords for search to display images:
    ~~~~
    cat files.log | xargs -I % find . -name foo*%*.jpg | xargs feh
    ~~~~
- Watch memory usage 
    ~~~~
    watch free -g
    ~~~~
 - Copy public RSA key to remote server
     ~~~~
    scp $HOME/.ssh/id_rsa.pub nixcraft@server1.cyberciti.biz:~/.ssh/authorized_keys
    ~~~~
    
  - Create alias for remote server
    ~~~~
    echo "host_alias IP" > /etc/host.aliases
    echo "export HOSTALIASES=/etc/host.aliases" >> ~/.bashrc
    ~~~~
 
   - Undo committed changes
   
    `
    git reset HEAD~
    `
- Get unique file extensions in a directory and subdirs
    `
    find . -type f | perl -ne 'print $1 if m/\.([^.\/]+)$/' | sort -u
    `
- Search for these extensions and print filesizes
    `
    find . -type f \( -name ".m4a" -o -name "*.mp4" -o -name "*.mkv" -o -name "*.webm" -o -name "*.dashVideo" \) -exec du '{}' \;
    `
    Alternatively, use `-exec cp '{}' /path/to/dir/` in order to copy files recursively.
    


 # Database tricks
- Restoring a mongo db dump into a docker instance running mongo
    ~~~~ 
    sudo docker run -d -p 27017:27017 -v <local backup dir>:<docker dir> mongo

    docker exec -it <CONTAINER ID> bash -c 'mongorestore <docker dir>'
    ~~~~ 
    
-Printing the first field on the second line
    ~~~~
    docker container ls  | awk 'FNR == 2 {print $1}'
    ~~~~
    
- Saving the command output to variable, and output variable:
    ~~~~
    var1="$(docker container ls  | awk 'FNR == 2 {print $1}')"
    echo "$var1"
    ~~~~
   
# Linux admin tricks
- When mounting a new filesystem usig fstab, these are recommended options for normal users:    
    `auto,uid=1000,dmask=027,fmask=137,umask=002`
    `auto`: mounts on boot
    `uid=1000`: a user with uid 1000 is the first normal user (non-root user) created on the system
    `dmask`: permissions for directories
    `fmask`: permissions for files
    `umask`: permissions for all
- `iptables` configuration: How can I set up an iptables rule that blocks all incoming and outgoing traffic on all ports, except for localhost?
    ```bash
    sudo addgroup no-internet # add new user group
    # the command below may not work on some kernels (see https://www.man7.org/linux/man-pages/man8/iptables-extensions.8.html -> "owner)
    sudo iptables -A INPUT -m owner --gid-owner no-internet -j DROP # block all incoming traffic on all ports
    sudo iptables -A OUTPUT -m owner --gid-owner no-internet -j DROP # block all outgoing traffic on all ports 
    # the command below may not work on some kernels (see https://www.man7.org/linux/man-pages/man8/iptables-extensions.8.html -> "owner)
    sudo iptables -I INPUT -m owner --gid-owner no-internet -i lo -j ACCEPT # allow incoming traffic on localhost
    sudo iptables -I OUTPUT -m owner --gid-owner no-internet -o lo -j ACCEPT # allow outgoing traffic on localhost
    ```

    Then test via something like `sudo -g no-internet curl -XGET 127.0.0.1:8888`
    
    >Note: The `-I` option inserts the rule at the beginning of the chain, so it takes precedence over the -A option that appends the rule at the end of the chain. This way, the localhost traffic is allowed before the general blocking rules are applied.














