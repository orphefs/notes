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
    



# Python tricks
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
    

    



# Bash tricks
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
- Selectively copy files from server:
    ~~~~
    rsync -Rv -e ssh --include '*.json' --include '*.txt' --exclude='*' user@server:/path/to/data/ .
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

 

