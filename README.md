# ctfd-challenge-dependencies
Add dependencies to CTFd challenges. Verified working with CTFd version 1.2.0


![admin panel](imgs/admin-panel.png)


## Install

1. clone this repository to your CTFd installation under `CTFd/plugins/`
2. Start/restart your ctfd instance
3. Thats it. At this point you should find a plugin menu item called "Challenge dependencies" under your admin panel. From there you can add and remove dependencies to challenges. When a team loads the challenge page, only challenges with satisfied dependencies will be shown

## Developer notes

I tried to make this plugin as un-intrusive as possible. Meaning it manipulates as little as possible of pre existing routes and database structure. Hopefully this will make it easier to maintain with future CTFd versions.

The only API endpoint which is overwritten with a custom plugin function is `/chals` (only returns challenges which meets its dependencies).

A wrapper function is also added to some other functions to prevent access to challenges with unmet dependencies. See the [load function](src/__init__.py) to fund out which ones.

No pre existing database tables are manipulated. But a new table `dependencies` is added.
