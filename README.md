# m02-export-vk-comments
Exports comments of a given club posts. Runs as a docker container

## How to install

Clone the repository and go the directory.

    git clone git@github.com:dimdasci/m02-export-vk-comments.git

    cd m02-export-vk-comments

Run `build` command to build docker image.

    make build

## How to run

Use `run` command with arguments to export posts and comments. The data exported will be saved at `data` directory.

Arguments:
- CLUB_ID — id of a VK club to export from.
- d — a number of days from now to export posts, by default is 1.
- f — a filter as a string. If given only posts containing that string will be exported.

### Examples of running

Export posts for the last 7 days containing 'как ваше самочувствие' and its comments

    make run ARGS="87598739 -d 7 -f 'как ваше самочувствие'"

Exports all posts for a last 24 hours

    make run ARGS=87598739

Get help on running the script

    make run


## TO DO

- Export threaded comments
- Manage posts and comments number greater then 100
- Add timestamp to data file names
- Use Logger to report
- Write tests 