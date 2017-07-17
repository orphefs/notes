# notes
Some useful scripting / linux  / coding tricks I've collected along the way

# Git tricks
#### Renaming a git branch
Here are the steps to rename the branch:

1. switch to branch which needs to be renamed
2. git branch -m <new_name>
3. git push origin :<old_name>
4. git push origin <new_name>:refs/heads/<new_name>


# Bash tricks
- cat \`ls | grep .confusionmatrix`

