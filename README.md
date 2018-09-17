# Timed Releases
Adds timed releases to CTFd challenges.

Participants can see when a challenge will be released. The challenge's data will only be visible once the time has
elapsed.

This plugin has been tested with CTFd version 1.2.0. It is recommended to combine this plugin with
DynamicValueChallenge.

![admin panel](imgs/admin-panel.png)


## Install

1. clone this repository to your CTFd installation under `CTFd/plugins/`
2. Start/restart your ctfd instance
3. Thats it. At this point you should find a plugin menu item called "Challenge Timed Releases" under your admin panel.
   From there you can set (or remove) the release time for a challenge.

## Limitations

* only supports timed releases of the challenges. Hints aren't supported.
* once set, can't remove a timed release.

## Developer notes

This plugin's code was written by forking [ctfd-challenge-dependencies](https://github.com/narhen/ctfd-challenge-dependencies).

We tried to keep the same philosophy of making the plugin as un-intrusive as possible.

No pre existing database tables are manipulated. But a new table `timed_releases` is added.
